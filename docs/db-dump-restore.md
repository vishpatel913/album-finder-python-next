# DB dump / restore — enriched data as source of truth

Self-assigned task list. Goal: **manually export the current DB to a file in
`dumps/`, and on startup import that file if it exists, else fall back to seed.**
So after a `make nuke` you get your enriched data straight back, and `make seed`
still works independently.

Boot logic to end up with:

```
alembic upgrade head            # schema (unchanged)
if dumps/<dump> exists:  import it
else:                    seed from Library.xml
```

---

## Approach — recommended

**App-level JSON export/import via the existing repos** (not `pg_dump`). Why it
fits here:

- Reuses the repos' `upsert` ([domain/artist/repository.py](backend/domain/artist/repository.py)) — **idempotent**, so re-running on a populated DB is safe (no "is the DB empty?" guard needed, and it mirrors how `seed` already behaves).
- No Postgres client tools in the api image, no schema/migration coupling — Alembic still owns the schema; the dump is just rows.
- Same shape as the existing `python -m scripts.seed` entrypoint step.
- Human-readable, diffable artifact (even though gitignored).

Trade-off: not a byte-exact backup (only what the models serialise). Fine for
"recover my enriched data". If you'd rather have an exact native backup, see the
`pg_dump` alternative at the bottom.

**Dump location:** `dumps/music_library.json`. `dumps/` is already gitignored
(`/dumps/*` + `!.gitkeep`) and mounted into the api container at `/data` — so
the entrypoint reads it at `/data/music_library.json`.

**Write it from the host, not inside the container** (the `pg_dump > file`
pattern). The export script streams JSON to **stdout**; the Make target
redirects that into `dumps/` on the host. So the file is written by the host
into the repo, and the mount stays **read-only** (`./dumps:/data:ro` in
[docker-compose.yml](docker-compose.yml)) — no writable mount, no compose change.
The container only ever *reads* `/data` (on boot import); it never writes there.

---

## Format & performance

Is JSON the fastest format for large ingest? **No — but it doesn't matter at
this scale, and the format isn't where the time goes.** The bottleneck is the DB
write path (per-row ORM upsert + flush/commit round-trips), not JSON parsing.
This dump is artists + albums (tracks currently disabled) — a few thousand rows,
smaller than the 23 MB the `Library.xml` weighs. Parsing that is milliseconds.
**Ship plain JSON; don't pre-optimise a few-thousand-row load.**

If import ever feels slow, reach for these **in order** — format is last:

1. **Batch the writes.** One transaction, commit once. The import script already
   does artists → flush → albums → flush → tracks → commit; keep it that way.
   Avoid any per-row commit.
2. **Bulk insert / `COPY`.** For genuinely large loads, Postgres `COPY` (via
   `psycopg`) is roughly an order of magnitude faster than row-by-row INSERTs.
   The post-`nuke` restore is the ideal case: tables are **empty**, so no upsert
   conflict-handling is needed — `COPY` straight in. Trade-off: this is a
   "restore into empty DB" fast path that gives up the idempotent-re-run
   property, so it'd live alongside (not replace) the upsert import.
3. **Then the file format**, if still needed:
   - **`orjson`** instead of stdlib `json` — several times faster, near drop-in
     (was already a dependency in the old `functions/venv`).
   - **JSONL** (one JSON object per line) instead of one big array — lets you
     *stream* row-by-row at constant memory and feed batched inserts, instead of
     loading the whole file into RAM. The real scalability win, and it stays
     greppable/debuggable.

Binary formats (msgpack, parquet, pickle) are faster/smaller but cost
readability and add deps — not worth it for a personal, occasionally-eyeballed
source-of-truth artifact.

**Recommendation:** plain JSON now → batched inserts / `COPY`-into-empty-DB if it
gets slow → `orjson` + JSONL only if you outgrow that.

---

## Tasks

### 1. Export script — ⬜
`backend/scripts/export_db.py`
- [ ] Open a session (`session_scope` from [infrastructure/database/session.py](backend/infrastructure/database/session.py)).
- [ ] Read all rows via the repos' `.list()` (artist, album, track).
- [ ] Serialise with SQLModel `.model_dump()`; wrap as `{"version": 1, "artists": [...], "albums": [...], "tracks": [...]}`.
- [ ] Write the JSON to **stdout** (`json.dump(data, sys.stdout, default=str)`) — the host redirect captures it into `dumps/`.
- [ ] Send any logs/counts to **stderr** (`print(..., file=sys.stderr)`) so they don't corrupt the JSON stream. Watch [session.py](backend/infrastructure/database/session.py) `create_engine(echo=True)` — SQL logging goes to stderr by default (fine), but confirm nothing lands on stdout.

### 2. Import script — ⬜
`backend/scripts/import_db.py` (model it on [application/ingestion/service.py](backend/application/ingestion/service.py) `seed_library`)
- [ ] Read the JSON at `argv[1]`.
- [ ] Upsert in FK order: artists, albums → `session.flush()`, then tracks → `commit()`.
- [ ] Use `Model.model_validate(row)` + `repo.upsert(...)`.
- [ ] No-op cleanly if the file is missing (let the entrypoint decide the fallback).

> Note: `seed` currently has track ingestion commented out ([service.py](backend/application/ingestion/service.py)). Decide whether the dump includes tracks now or once track ingestion is enabled (see [functions-to-backend-migration.md](functions-to-backend-migration.md)).

### 3. Make targets — ⬜
Add to the root [Makefile](Makefile) under the Database section:
- [ ] `db-export` — stream to stdout, host redirects into the repo (`-T` disables the pseudo-TTY so the stream isn't mangled):
  ```make
  db-export: ## Export the DB to dumps/music_library.json
  	docker compose run --rm -T --entrypoint python api -m scripts.export_db > dumps/music_library.json
  ```
- [ ] `db-import` — manual restore (reads the read-only `/data` mount, fine):
  ```make
  db-import: ## Import dumps/music_library.json into the DB
  	docker compose run --rm --entrypoint python api -m scripts.import_db /data/music_library.json
  ```
- [ ] Keep `seed` as-is (independent, per the goal).

### 4. Boot logic — ⬜
Edit [backend/entrypoint.sh](backend/entrypoint.sh) — replace the seed step with import-else-seed:
- [ ] After `alembic upgrade head`:
  ```sh
  if [ -f /data/music_library.json ]; then
    echo "==> Importing DB dump..."
    python -m scripts.import_db /data/music_library.json
  else
    echo "==> No dump found — seeding from Library.xml..."
    python -m scripts.seed
  fi
  ```
- [ ] (Optional) since import is idempotent it re-runs on every restart — harmless, but you can skip it when the DB already has rows if boot speed matters.

### 5. Verify — ⬜
- [ ] `make up` → enrich some data → `make db-export` → confirm `dumps/music_library.json` written.
- [ ] `make nuke && make up` → confirm it imports the dump (not seed) and the enriched data is back.
- [ ] Delete/rename the dump → `make up` → confirm it falls back to `seed`.
- [ ] `make seed` still works standalone.

---

## Alternative — native `pg_dump` / `pg_restore`

If you want an exact backup instead of app-level JSON:

- **Export** (host redirect, no compose/image change — runs in the `database` container which has the tools):
  ```
  docker compose exec -T database pg_dump -U postgres -Fc music_library > dumps/music_library.dump
  ```
- **Manual restore** (also native to the `database` container):
  ```
  cat dumps/music_library.dump | docker compose exec -T database pg_restore -U postgres -d music_library --data-only --no-owner
  ```
- **Boot auto-restore** is the catch: the entrypoint runs in the **api** container,
  which has no `pg_restore`. You'd need to add `postgresql-client` (matching
  server v16) to the runtime stage of [backend/Dockerfile](backend/Dockerfile) and
  set `PGPASSWORD`, then `pg_restore -h database ... /data/music_library.dump`.
- **Downsides vs app-level:** not idempotent (conflicts on a non-empty DB, so you
  need an emptiness guard), and the image change above. Byte-exact is the upside.

Recommendation stands: **app-level JSON** unless you specifically need exact backups.
