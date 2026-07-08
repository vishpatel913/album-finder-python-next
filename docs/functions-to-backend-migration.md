# `functions/` → `backend/` migration

Salvage checklist for the old serverless prototype (`functions/`) now that
`backend/` is the MVP. Work through the items **one at a time** — each has a
_Relevance_ line to assess before doing it, plus specific source → target
pointers so it can be picked up cold.

`functions/` is ~90% stale (serverless scaffolding, `venv/`, duplicate read
endpoints, old `SpotifySearch`). Only the four items below hold logic the MVP is
missing. Once items 1–3 are lifted, **the whole `functions/` directory can be
deleted** (see item 5).

Status key: ⬜ not started · 🔄 in progress · ✅ done · 🗑️ decided against

---

## 1. Spotify user-OAuth + follow/save write actions — ⬜

**Relevance: HIGH.** Backend has this only as stubs. Biggest genuine gap.
Assess: do we want "like" (follow artist / save album) in the MVP now, or defer?

Backend today:
- [backend/infrastructure/auth/spotify_oauth.py](backend/infrastructure/auth/spotify_oauth.py) — `authorize_url` / `exchange_code` / `refresh` all `raise NotImplementedError`.
- [backend/api/auth.py](backend/api/auth.py) — `get_current_user` always raises 501.
- [backend/application/ports/identity.py](backend/application/ports/identity.py) — `IdentityPort` exists, no adapter.

Working reference in `functions/`:
- [functions/api/deps.py](functions/api/deps.py) — `get_spotify_user()`, `_user_auth_manager()`, `user_token_cache_path()`: the out-of-band consent + cached-refresh-token pattern (headless server, `open_browser=False`).
- [functions/api/routes/spotify.py](functions/api/routes/spotify.py) — `GET /library/contains` (initial like-state, chunked 50 artist / 20 album) and `POST /library/toggle` (follow/unfollow, save/remove).

TODO:
- [ ] Decide scope: full OAuth flow now, or just port the follow/save calls behind the existing client-credentials setup.
- [ ] Implement `SpotifyOAuth` (or wrap spotipy's `SpotifyOAuth` as the old code did) with token persistence.
- [ ] Add a user-authorised client provider in `backend/api/dependencies.py` (mirror `get_enrichment_service`).
- [ ] Add `contains` + `toggle` endpoints — likely a new `backend/api/routes/library.py` or fold into `search`/a new `spotify` router. Follow DDD: route → application command → port.
- [ ] Extend `MusicEnrichmentPort` (or a new `LibraryPort`) with follow/save/contains, implement in `infrastructure/spotify`.
- [ ] Port the one-time consent script → `backend/scripts/spotify_authorize.py`.
- [ ] Re-point [docs/spotify-write-access.md](docs/spotify-write-access.md) at the new backend — it currently documents the **old** `functions/` impl (`functions/venv`, `/api/spotify/...` paths). Its dashboard-setup + FE-wiring sections are still valid.

---

## 2. Rich parser logic + no-match crash guard — ⬜

**Relevance: HIGH.** Contains a live-crash fix (see 2a). The rest is feature
logic the MVP parser dropped — assess per sub-item; ingestion is the natural
time to do this. Backend parser: [backend/libs/music_library/parser.py](backend/libs/music_library/parser.py). Source: [functions/resources/music_library.py](functions/resources/music_library.py).

### 2a. No-match guard on enrichment — ⬜
**Do this regardless — it's a bug, not a feature.** [backend/application/artists/commands.py](backend/application/artists/commands.py) and [backend/application/albums/commands.py](backend/application/albums/commands.py) take `results[0]` with no empty check → `IndexError`/500 on any unmatched artist/album. Old resolvers fail soft and cache the miss ([functions/resources/artist_resolver.py](functions/resources/artist_resolver.py), [functions/resources/album_resolver.py](functions/resources/album_resolver.py)).
- [ ] Guard both `enrich_*` commands against empty search results; return `None`.

### 2b. Compilation / Various-Artists regrouping — ⬜
Group comp tracks under the real performer, not a junk "Various Artists" bucket. Source: `_group_artist`, `VARIOUS_ARTISTS_MARKERS`.
- [ ] Port into the parser's per-track artist resolution.

### 2c. Featured-artist extraction — ⬜
Backend has this **commented out** at [backend/libs/music_library/parser.py:24](backend/libs/music_library/parser.py#L24). Source: `_extract_featured`, `_split_featured`, `_FEATURED_RE`, `_FEATURED_SPLIT_RE`.
- [ ] Port regexes; decide where `featured` / `featured_artists` land in the track model + DB.

### 2d. Near-duplicate artist detection — ⬜
Surfaces "Beyoncé" vs "Beyonce" case/accent/whitespace variants. Source: `find_near_duplicate_artists`, `_normalise` (NFKD + ASCII fold + casefold).
- [ ] Port as a utility; expose via a route or ingestion warning.

### 2e. Greatest-hits detection + enrichable filters — ⬜
Source: `_GREATEST_HITS_RE`, `enrichable_albums`, `enrichable_artist_names` (skip compilation-only artists / greatest-hits albums when enriching).
- [ ] Port if we want to avoid burning Spotify calls on comps/hits.

### 2f. Per-artist / per-album rollups — ⬜
top_genre, all_genres, year_min/max, avg_rating, loved_count, play totals. Source: `_artist_rollup`, `_album_rollup`. MVP computes none of these.
- [ ] Assess vs current DTOs — may be superseded by DB queries, or worth precomputing at ingest.

### 2g. Library snapshot/backup — ⬜
Timestamped, idempotent (mtime-keyed) backup of `Library.xml`. Source: `snapshot_library`.
- [ ] Port into ingestion if we want auto-backups on seed.

---

## 3. Spotify client hardening — ⬜

**Relevance: MEDIUM, quick win.** Backend's spotipy client has **no timeout and
no retries** ([backend/infrastructure/spotify/client.py](backend/infrastructure/spotify/client.py)) — it can hang indefinitely — and Spotify errors aren't mapped to HTTP responses.

Source: [functions/api/deps.py](functions/api/deps.py) (`requests_timeout=10, retries=2`) and [functions/api/main.py](functions/api/main.py) (exception handlers → clean 503s).

TODO:
- [ ] Add `requests_timeout` + `retries` when constructing `spotipy.Spotify` in `SpotifyEnrichmentClient.__init__`.
- [ ] Add FastAPI exception handlers for `SpotifyException` / `SpotifyOauthError` / missing-creds → 503 with `detail`. Wire in `backend/main.py`.

---

## 4. Keep as reference — do NOT port yet — ⬜

**Relevance: LOW now, revisit when match quality bites.**
- **Artist override concept** — [functions/resources/artist_overrides.py](functions/resources/artist_overrides.py) (inert stub). Design: `search_as` (alt search term) / `spotify_id` (pin exact entity) for wrong/ambiguous matches. Backend has no scored matching, so this becomes relevant once bad matches appear.
- **Filter/sort query surface** — [functions/api/routes/library.py](functions/api/routes/library.py) + [functions/api/schemas.py](functions/api/schemas.py) document the query params the old FE expected (`genre`, `vibe`, `year_from/to`, `added_after`, sort enums). Backend serves DB-backed DTOs instead, but this is a useful spec of FE expectations.
- **Spotify enrichment fields** — old `ArtistResolver` captured `genres`, `popularity`, `followers`; backend's [enrichment_types.py](backend/application/ports/enrichment_types.py) `Artist` does not. The old FE "vibe" filter needed Spotify genres — add these fields if that feature returns.
- [ ] (No action — checkbox to mark once consciously reviewed.)

---

## 5. Delete `functions/` — ⬜

**Do last, only after 1–3 are lifted.**
- [ ] Confirm items 1–3 done and item 4 reference notes captured elsewhere.
- [ ] Confirm nothing in `frontend/` or `docker-compose.yml` still points at `functions/` (old docs/scripts reference `functions/venv`).
- [ ] `git rm -r functions/`.

Explicitly discardable (no salvage): `functions/resources/spotify.py` (old `SpotifySearch`, hardcoded `year:2020` + a personal email), `functions/handlers/`, `functions/serverless.yml`, `functions/setup.py`, `functions/run.py`, `functions/venv/`, lock files.
