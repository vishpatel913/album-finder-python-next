# Album Finder

Parses your Music.app library, ranks artists/tracks by play count, enriches
with Spotify images and "vibe" tags, and serves it through a FastAPI
backend + Next.js App Router frontend.

Two ways to run: **Docker** (one command, everything wired up) or
**bare-metal** (two terminals, more control while learning).

---

## Prerequisites

| Tool | Version | Why |
| ---- | ------- | --- |
| Python | 3.11+ | FastAPI + parser |
| Node | 20+ | Next.js 14 |
| Docker Desktop | latest | Optional — for `docker compose up` |
| Spotify dev creds | — | https://developer.spotify.com/dashboard → create app |
| Music.app `Library.xml` | — | File → Library → Export Library… in Music.app |

If you don't have a real `Library.xml` to hand, use the committed
[`fixtures/sample_library.xml`](fixtures/sample_library.xml) — it covers
every code path (genres, ratings, loved, near-dupes, fallbacks).

---

## 1. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```dotenv
# Path on the HOST to your Library.xml. Defaults to ~/Music/Library.xml.
MUSIC_LIBRARY_XML_HOST_PATH=~/Music/Library.xml

# Spotify (Client Credentials flow — read-only, no user OAuth)
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
```

To test against the fixture without a real export:

```dotenv
MUSIC_LIBRARY_XML_HOST_PATH=./fixtures/sample_library.xml
```

---

## 2A. Run with Docker (recommended)

```bash
docker compose up --build
```

That's it. Two services come up:

- **api**  → http://localhost:8000 (FastAPI, auto-reload off)
- **web**  → http://localhost:3000 (Next.js dev server)

Open http://localhost:3000 and you should see your artist count on the
home page. Hit `/artists` and `/tracks` to browse.

Sanity-check the API directly:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/library/facets
curl "http://localhost:8000/api/library/artists?limit=5"
```

Auto-generated OpenAPI docs: http://localhost:8000/docs

To stop:

```bash
docker compose down
```

---

## 2B. Run bare-metal (two terminals)

Useful when you're iterating on Python or the FastAPI routes and want
faster reload than the container.

### Terminal 1 — FastAPI backend

```bash
cd functions

# Fresh venv (one-time setup)
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run it
export MUSIC_LIBRARY_XML=../fixtures/sample_library.xml   # or your real export
export SPOTIPY_CLIENT_ID=...
export SPOTIPY_CLIENT_SECRET=...
uvicorn api.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
INFO api.deps: Parsing /path/to/Library.xml (mtime=...)
INFO resources.music_library: Parsed N artists from /path/to/Library.xml
```

### Terminal 2 — Next.js frontend

```bash
# From repo root
npm install        # or `yarn`

export API_BASE=http://localhost:8000
npm run dev        # or `yarn dev`
```

Open http://localhost:3000.

---

## 3. CLI: pre-compute albums.json (legacy / optional)

The original Spotify-search pipeline still works as a one-shot CLI. It
reads the library, hits Spotify for each top artist's recent albums, and
writes `data/albums.json`.

```bash
cd functions
source venv/bin/activate

# Defaults to ~/Music/Library.xml — override with --library or env var
python run.py --library ../fixtures/sample_library.xml
# or
python run.py ../fixtures/sample_library.xml   # bare positional path
# or
MUSIC_LIBRARY_XML=../fixtures/sample_library.xml python run.py
```

Expected output ends with:

```
INFO run: Top N artists by play count selected
... Spotify search logs per artist ...
INFO run: Saved to data/albums.json
```

This path is independent of the FastAPI server.

---

## 4. Common commands

| What | Command |
| ---- | ------- |
| Bring up Docker stack | `docker compose up --build` |
| Tear down | `docker compose down` |
| Rebuild after Python deps change | `docker compose build api` |
| Rebuild after Node deps change | `docker compose build web` |
| View logs | `docker compose logs -f api` / `web` |
| Run Python CLI (bare-metal) | `cd functions && python run.py --library …` |
| Run FastAPI (bare-metal) | `cd functions && uvicorn api.main:app --reload` |
| Run Next.js (bare-metal) | `npm run dev` |
| TypeScript check | `npm run typecheck` |
| Force re-parse library | `curl -X POST http://localhost:8000/api/library/refresh` |
| Bulk-enrich Spotify cache | `curl -X POST http://localhost:8000/api/spotify/enrich -H 'content-type: application/json' -d '{"names":["Radiohead","Burial"]}'` |

---

## 5. What lives where

```
.
├── app/                       # Next.js App Router (frontend)
│   ├── layout.tsx             # root layout + nav
│   ├── page.tsx               # home (health + dupe warnings)
│   ├── artists/page.tsx       # top artists, server component, URL filters
│   ├── tracks/page.tsx        # top tracks, server component, URL filters
│   ├── components/Filters.tsx # client component — pushes filters into URL
│   ├── components/ArtistTile.tsx, TrackRow.tsx
│   └── lib/api.ts             # typed FastAPI client
│
├── functions/                 # Python backend
│   ├── api/                   # FastAPI app
│   │   ├── main.py            # entrypoint, CORS, /api/health
│   │   ├── deps.py            # singletons + mtime-keyed library cache
│   │   ├── schemas.py         # Pydantic models
│   │   └── routes/
│   │       ├── library.py     # /api/library/{artists,tracks,facets,…}
│   │       └── spotify.py     # /api/spotify/{artist,enrich}
│   ├── resources/
│   │   ├── music_library.py   # plistlib parser + near-dupe scanner
│   │   ├── artist_resolver.py # Spotify name → ID + image + genres, cached
│   │   ├── artist_overrides.py# inert stub for manual overrides
│   │   └── spotify.py         # legacy SpotifySearch wrapper (CLI uses it)
│   ├── handlers/              # legacy lambda-shape handler (still works)
│   ├── run.py                 # CLI: parse library → Spotify → albums.json
│   ├── Dockerfile             # api service image
│   └── requirements.txt
│
├── fixtures/sample_library.xml# Committable mock Music.app library
├── data/                      # Runtime artefacts (gitignored)
│   ├── spotify_artist_cache.json
│   └── albums.json
├── docker-compose.yml
├── Dockerfile.web
├── .env.example
└── .claude/plans/             # Plan docs for past/future work
```

---

## 6. Troubleshooting

**`Library XML not found`** — check `MUSIC_LIBRARY_XML` (bare-metal) or
`MUSIC_LIBRARY_XML_HOST_PATH` (Docker). The path must be absolute or
relative to the directory you launched from. With Docker, the file is
mounted read-only at `/library/Library.xml` inside the container.

**Home page shows "API unreachable"** — the FastAPI service isn't up, or
`API_BASE` isn't pointing at it. In Docker the web container resolves
`http://api:8000` via the compose network; bare-metal uses
`http://localhost:8000` by default.

**Spotify 401 / no images** — credentials missing or invalid. The
resolver fails soft (no image, no genres) but still returns the artist
row from the library. Check `functions/.env` or the host `.env`.

**Near-duplicate Album Artists banner** — the parser found artists that
collapse to the same name when you strip case/whitespace/accents (e.g.
`Beyoncé` vs `Beyonce`). Clean them up in Music.app for consistent
grouping; the banner disappears after re-export.

**Stale data after re-export** — the API caches the parsed library by
file mtime, so re-exporting in Music.app auto-invalidates. If it
doesn't, hit `POST /api/library/refresh`.

---

## 7. What's not built yet

- **Like button** — needs Spotify OAuth (Authorization Code + PKCE) for
  `user-library-modify` scope. The current client-credentials flow is
  read-only. Planned in a follow-up — see
  [`.claude/plans/next-app-router-fastapi-readonly.md`](.claude/plans/next-app-router-fastapi-readonly.md).
- **Tests** — none yet. Parser is verified via the fixture; route
  handlers are unit-test-able via FastAPI's `TestClient`.
- **Production build** — `docker-compose.yml` runs the Next dev server.
  For prod, switch the web CMD to `npm run build && npm start`.
