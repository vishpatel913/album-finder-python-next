# Backend challenge list

A pick-and-play set of improvements to the backend, each chosen to **teach a
../backend/DDD concept while adding real value to the app**. They're independent —
roll a die, pick whatever you fancy. A few pair well (noted inline).

Your DDD skeleton (domain / application / infrastructure / api, repositories,
ports/adapters) is already sound, so these are *fill-in-the-shape* tasks, not
rewrites.

**Overarching resource:** [Architecture Patterns with Python](https://www.cosmicpython.com/)
(Percival & Gregory, free online) — written for almost exactly this stack.
Chapter refs below point into it.

Each card: **Teaches · Summary · Outcome · Starting points · Resources**. Tick
`⬜→✅` as you go.

| # | Challenge | Concept | Effort |
|---|---|---|---|
| 1 | Rich domain model | anemic vs rich models | 🟢 quick |
| 2 | Domain exceptions + handler | error boundaries | 🟢 quick |
| 3 | Typed settings | config / 12-factor | 🟢 quick |
| 4 | Unit of Work | transactions / patterns | 🟡 medium |
| 5 | Test the app layer with fakes | testing / hexagonal payoff | 🟡 medium |
| 6 | Harden enrichment | resilience / domain services | 🟡 medium |
| 7 | Pagination + query object | Specification pattern | 🟡 medium |
| 8 | Background / bulk enrichment | async work / batching | 🔴 meaty |

Suggested first roll: **3** (fast win), then the **5 + 6** pair (build the test
harness, then safely fix the crash), then **1** as your first real DDD refactor.

---

## 1. De-anemic the domain model — ⬜
**Teaches:** rich vs anemic domain models, Tell-Don't-Ask, where business rules live (Cosmic Python ch.1).

**Summary.** [domain/artist/model.py](../backend/domain/artist/model.py) already carries the comment *"Domain logic lives on the model, not scattered in routes"* with `total_albums()` / `total_tracks()` commented out. Right now enrichment mutates fields from the application layer — an anemic model. Move behaviour onto the aggregate.

**Outcome.** Commands orchestrate; the model owns its rules. `artist.apply_enrichment(spotify_artist)` lives on the model, tested in isolation with no DB or Spotify.

**Starting points.**
- [ ] Add `apply_enrichment(...)` to `Artist` (and `Album`); move the field-setting out of [application/artists/commands.py](../backend/application/artists/commands.py).
- [ ] Uncomment/implement `total_albums()` / `total_tracks()` as model methods.
- [ ] Have the enrich command call the model method, then `upsert`.

**Resources.** Cosmic Python ch.1 (Domain Modelling). No new libs.

---

## 2. Domain exceptions + one central handler — ⬜
**Teaches:** separating domain errors from transport, consistent error envelopes, DRY routes.

**Summary.** Each route repeats `try/except ValueError → 404` ([artists.py](../backend/api/routes/artists.py), [albums.py](../backend/api/routes/albums.py)). Define a small domain-error hierarchy and map it once.

**Outcome.** Routes stop catching `ValueError`; a single handler turns `ArtistNotFound` → 404, `EnrichmentUnavailable` → 503, etc., with a consistent JSON shape.

**Starting points.**
- [ ] `core/exceptions.py` (or `domain/errors.py`): `DomainError`, `NotFoundError`, ...
- [ ] Raise them from domain/application instead of `ValueError`.
- [ ] Register `@app.exception_handler(...)` in [main.py](../backend/main.py) mapping each to a status + envelope.
- [ ] (Pairs with #6 — Spotify errors → 503 land in the same place.)

**Resources.** [FastAPI — custom exception handlers](https://fastapi.tiangolo.com/tutorial/handling-errors/).

---

## 3. Typed settings with `pydantic-settings` — ⬜
**Teaches:** 12-factor config, validation-at-boot, secret handling.

**Summary.** [core/config.py](../backend/core/config.py) is a plain class reading `os.getenv`, with a comment inviting exactly this swap. Fail fast at startup if required config is missing.

**Outcome.** A `Settings(BaseSettings)` that validates on load — a missing `SPOTIPY_CLIENT_ID` errors clearly at boot, not mysteriously mid-request.

**Starting points.**
- [ ] Add `pydantic-settings` to `pyproject.toml`.
- [ ] Convert `Settings` to `BaseSettings`; type each field; mark required vs optional.
- [ ] Load `.env`; keep the single `settings` instance import surface.
- [ ] Bonus: split `DevSettings` / `TestSettings` off `ENVIRONMENT`.

**Resources.** [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

---

## 4. Explicit Unit of Work — ⬜
**Teaches:** transaction boundaries, the UoW pattern, decoupling use cases from the ORM session.

**Summary.** `session_scope` in [session.py](../backend/infrastructure/database/session.py) is a proto-UoW. Formalise it so application commands depend on a `UnitOfWork` (exposes repos + `commit`/`rollback`) rather than handling sessions directly.

**Outcome.** A command reads like `with uow: uow.artists.upsert(a); uow.commit()`. Transaction control lives in one place; commands get trivial to test with a fake UoW.

**Starting points.**
- [ ] `application/unit_of_work.py`: `AbstractUnitOfWork` + a SQLModel impl wrapping a session and the repos.
- [ ] Refactor [ingestion/service.py](../backend/application/ingestion/service.py) and the enrich commands to use it.
- [ ] Provide it via `Depends` in [dependencies.py](../backend/api/dependencies.py).

**Resources.** Cosmic Python ch.6 (Unit of Work).

---

## 5. Test the application layer against fakes — ⬜
**Teaches:** the testing pyramid, dependency inversion made concrete, *why* ports/adapters exist.

**Summary.** The point of your ports is that you can test `enrich_artist` with a `FakeEnrichmentPort` — no Spotify, no network. Stand up a `tests/` layer.

**Outcome.** Fast unit tests over commands/domain with in-memory fakes; a handful of repo tests against a throwaway DB; a couple of API tests via `TestClient`. `make test` becomes meaningful.

**Starting points.**
- [ ] `tests/fakes.py`: `FakeEnrichmentPort(MusicEnrichmentPort)` returning canned results (incl. the *empty* case — sets up #6).
- [ ] Unit-test the enrich command + any domain methods (from #1) with the fake.
- [ ] Repo tests against SQLite or a disposable Postgres (see testcontainers).
- [ ] API smoke tests with FastAPI `TestClient` / `httpx`.

**Resources.** [pytest](https://docs.pytest.org/), [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/), [testcontainers-python](https://testcontainers-python.readthedocs.io/), optional [factory-boy](https://factoryboy.readthedocs.io/). Cosmic Python ch.3 & 5.

---

## 6. Harden the enrichment path — ⬜
**Teaches:** defensive boundaries around external systems, domain services, value objects.

**Summary.** Two real weaknesses: the enrich commands take `results[0]` with no empty-check (crashes on any unmatched name), and [infrastructure/spotify/client.py](../backend/infrastructure/spotify/client.py) has no timeout/retries. Fix both — ideally introduce a `MatchingService` that *scores* candidates instead of trusting the top hit blindly.

**Outcome.** No 500s on unmatched artists/albums; Spotify calls time out and retry; matches are chosen by a score, not position. (Cross-refs [functions-to-backend-migration.md](functions-to-backend-migration.md) items 2a & 4.)

**Starting points.**
- [ ] Guard empty results in [artists/commands.py](../backend/application/artists/commands.py) + [albums/commands.py](../backend/application/albums/commands.py) → return `None`.
- [ ] Add `requests_timeout` + `retries` when constructing `spotipy.Spotify`.
- [ ] `domain/matching/service.py`: score candidates (name similarity, etc.), return best + confidence — a real domain service, unlike the current trivial pass-throughs.
- [ ] Consider a `MatchScore` value object.

**Resources.** [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz) (fast fuzzy scoring), [tenacity](https://tenacity.readthedocs.io/) (retry policy), spotipy `requests_timeout`/`retries` args.

---

## 7. Pagination + a query/specification object — ⬜
**Teaches:** the Specification / Query-Object pattern, response envelopes, keeping filtering out of routes.

**Summary.** `GET /artist/` returns everything ([artists.py](../backend/api/routes/artists.py)). The old `functions/` code had a rich filter/sort surface (genre, year range, "vibe", sort enums) — a ready-made spec. Add pagination and a query object that maps params → a domain query.

**Outcome.** List endpoints take `limit`/`cursor` (or page/size) and structured filters; the repo consumes a query/spec object instead of ad-hoc kwargs; responses carry paging metadata.

**Starting points.**
- [ ] Decide cursor vs offset (cursor scales better; offset is simpler).
- [ ] `ArtistQuery` / `AlbumQuery` objects (filters + sort + page); repo `list(query)`.
- [ ] Lift the filter/sort surface from [functions/api/routes/library.py](functions/api/routes/library.py) as the spec.
- [ ] Return an envelope: `{ items, total, next_cursor }`.

**Resources.** [fastapi-pagination](https://uriyyo-fastapi-pagination.netlify.app/) (optional), Specification pattern (Cosmic Python ch.7 hints), SQLModel `select().limit().offset()`.

---

## 8. Background / bulk enrichment — ⬜
**Teaches:** async work, idempotency, batching external I/O.

**Summary.** Enrichment runs synchronously in-request, one entity at a time. Add a bulk endpoint that batches Spotify calls (their `artists?ids=` takes up to 50) and runs off the request.

**Outcome.** "Enrich my whole library" kicks off without blocking; batched, idempotent (skips already-enriched), resumable. (Mirrors the old `resolve_many` in [functions/resources/artist_resolver.py](functions/resources/artist_resolver.py).)

**Starting points.**
- [ ] A bulk application command that batches ids (chunks of 50) and upserts results.
- [ ] Extend the enrichment port/adapter with a batch `get_artists(ids)`.
- [ ] Run it via FastAPI `BackgroundTasks` first; graduate to a task queue if you want durability.
- [ ] Make it idempotent — skip entities already enriched.

**Resources.** [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/); task queues: [arq](https://arq-docs.helpmanual.io/) (asyncio + Redis, lightweight), [taskiq](https://taskiq-python.github.io/), or Celery/Dramatiq (heavier). Spotify batch endpoints (`/artists?ids=`, `/albums?ids=`).

---

*Related docs:* [functions-to-backend-migration.md](functions-to-backend-migration.md) · [spotify-write-access-backend.md](spotify-write-access-backend.md) · [db-dump-restore.md](db-dump-restore.md)
