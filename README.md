# Album Finder

Parses your Music.app library, ranks artists/albums/tracks by play count, and
enriches with Spotify data. Local-only.

Two services, wired together by `docker-compose.yml`:

| Path | What | Stack |
| --- | --- | --- |
| [backend/](backend/) | REST API + parser + DB access | FastAPI · SQLModel · Postgres |
| [frontend/](frontend/) | Browse / search / edit UI | Vite · React · TanStack · Tailwind v4 |
| [functions/](functions/) | Spotify enrichment (serverless) | Python · Serverless Framework |

See each directory's own README for details.

---

## Quick start

```bash
cp .env.example .env        # add your Spotify creds (see below)
make install                # frontend deps
make up                     # db + api + web, all in Docker
```

- Frontend → http://localhost:5173
- API docs → http://localhost:8004/docs
- pgAdmin → http://localhost:5050 (`admin@admin.com` / `admin`)

Faster FE loop — run the backend in Docker, the frontend on the host:

```bash
make backend                # db + api only
make dev                    # Vite dev server with HMR
```

Run `make` to see every target.

---

## Configuration

`.env` (see [.env.example](.env.example)) holds the Spotify credentials and the
path to your Music.app `Library.xml` export. No real library to hand? The
committed [fixtures/sample_library.xml](fixtures/sample_library.xml) covers
every code path.

Get Spotify creds at https://developer.spotify.com/dashboard.

---

## Layout

```
album-finder/
├── backend/        FastAPI service
├── frontend/       Vite + React SPA
├── functions/      Spotify enrichment (serverless)
├── scripts/        Python helpers (test library, Spotify OAuth)
├── data/ dumps/ fixtures/   library exports, caches, samples
├── pgadmin/        pre-registered pgAdmin server
├── docker-compose.yml
├── Makefile        dev entrypoints — `make help`
└── .vscode/album-finder.code-workspace   multi-root workspace
```

## Editor

Open [.vscode/album-finder.code-workspace](.vscode/album-finder.code-workspace)
as a workspace so Pylance and the TS server scope to their own service. VS Code
will prompt to install the recommended extensions (Python, ruff, Tailwind,
Docker, EditorConfig).
