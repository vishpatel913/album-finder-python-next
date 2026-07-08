# Spotify write access (backend) — follow artists, save albums

Design doc for adding user-authorised "like" actions to `backend/`. This is a
**plan to build**, not a usage guide — endpoint names and script paths below are
proposed and get finalised as it's implemented.

**Outcome (unchanged from the old prototype):** a "like" toggles
**artist → follow** and **album → save** on the user's real Spotify account.
Tracks are out of scope (no Spotify track IDs yet).

**What's different from the old `functions/` version:** that one was
single-user with a file-cached token. This targets a **proper user table +
per-user tokens in the DB**, going through the same ports/adapters/commands the
rest of the backend uses.

---

## 1. Current state — the stubs this fills

Everything needed is scaffolded and unimplemented:

| File | State |
|---|---|
| [backend/infrastructure/auth/spotify_oauth.py](backend/infrastructure/auth/spotify_oauth.py) | `SpotifyOAuth.authorize_url` / `exchange_code` / `refresh` — all `NotImplementedError` |
| [backend/core/security.py](backend/core/security.py) | `create_access_token` / `decode_access_token` — `NotImplementedError` (for our own session JWT) |
| [backend/api/auth.py](backend/api/auth.py) | `get_current_user` guard — raises 501 |
| [backend/application/ports/identity.py](backend/application/ports/identity.py) | `IdentityPort` + `CurrentUser` — no adapter |
| [backend/core/config.py](backend/core/config.py) | already reads `SPOTIPY_CLIENT_ID/SECRET`, `SPOTIFY_REDIRECT_URI` |

Read-side enrichment already works via [SpotifyEnrichmentClient](backend/infrastructure/spotify/client.py) (client-credentials). Writes need a **user token**, which client-credentials can't provide — hence the OAuth auth-code flow below.

---

## 2. Key design decision — token persistence

The one real divergence from the old impl. Two layers of token:

1. **Spotify tokens** (access + refresh) — per user, stored in the DB. spotipy
   refreshes the access token using the refresh token; we persist the rotation.
2. **Our own session token** (JWT) — how the browser identifies itself to
   *our* API after connecting Spotify. Encoded/decoded via `core/security.py`.

Proposed tables (SQLModel, mirroring [domain/artist/model.py](backend/domain/artist/model.py) — `Base`/`table=True` split, string PK):

```python
# domain/user/model.py
class UserBase(SQLModel):
    spotify_user_id: str = Field(unique=True, index=True)   # Spotify's account id
    display_name: str | None = None
    email: str | None = None

class User(UserBase, table=True):
    id: str = Field(primary_key=True)   # our id (slugify/uuid)

# domain/user/model.py (or a dedicated spotify_account table)
class SpotifyAccount(SQLModel, table=True):
    user_id: str = Field(primary_key=True, foreign_key="user.id")
    access_token: str
    refresh_token: str
    expires_at: datetime
    scope: str
```

**Decision to make:** one-user personal app vs genuine multi-user.
- *Personal:* one `User` row, tokens in the DB, skip our-own-JWT (trust a single
  session). Simplest.
- *Multi-user:* full flow below (JWT session, per-user token lookup). You said
  you'd like the full user-table piece — this doc assumes that, but it degrades
  cleanly to personal.

**Encrypt tokens at rest?** Refresh tokens are long-lived credentials. For a
personal app, plaintext in your own DB is defensible; for anything shared,
encrypt (`core/security.py` is the home for that). Flag for review.

---

## 3. Components to build (by layer)

Follows the existing DDD wiring: route → application command → port → adapter,
repos injected via `api/dependencies.py`.

### Domain
- [ ] `domain/user/model.py` — `User` (+ `SpotifyAccount`) SQLModel tables.
- [ ] `domain/user/repository.py` — `AbstractUserRepository` + `SqlUserRepository` (mirror [artist/repository.py](backend/domain/artist/repository.py): `get_by_id`, `get_by_spotify_id`, `upsert`, token read/write).
- [ ] Alembic migration for the new tables (see [alembic-setup.md](docs/alembic-setup.md)).

### Application (ports + use cases)
- [ ] Extend `IdentityPort` / implement an adapter that resolves our session JWT → `CurrentUser`.
- [ ] New `LibraryWritePort` (or extend `MusicEnrichmentPort`) with: `is_following` / `follow` / `unfollow` (artist), `is_saved` / `save` / `remove` (album), `contains_many`.
- [ ] `application/auth/commands.py` — `begin_oauth()` (build authorize URL + state), `complete_oauth(code)` (exchange → upsert user + tokens → mint our JWT).
- [ ] `application/library/commands.py` — `toggle_like(user, type, id, action)`, `contains(user, type, ids)`.

### Infrastructure
- [ ] Implement `SpotifyOAuth` in [infrastructure/auth/spotify_oauth.py](backend/infrastructure/auth/spotify_oauth.py): `authorize_url(state)`, `exchange_code(code)`, `refresh(refresh_token)`. Wrap spotipy's `SpotifyOAuth` or hit the token endpoint directly.
- [ ] A **user-authorised** Spotify client provider — build a per-request `spotipy.Spotify` from the user's stored access token, auto-refreshing via the repo when expired. Distinct from `get_enrichment_service()`.
- [ ] Implement the `LibraryWritePort` adapter over that client (chunk contains: **50 artist / 20 album** per Spotify request).
- [ ] Implement `core/security.py` JWT encode/decode (PyJWT) for our session token.

### API
- [ ] `api/auth.py` — finish `get_current_user` (bearer → decode JWT → user).
- [ ] `api/dependencies.py` — `get_user_repo`, `get_spotify_user_client`, `get_library_write_service`.
- [ ] `api/routes/auth.py` — `GET /auth/spotify/login` (302 → Spotify), `GET /auth/spotify/callback` (exchange, set session), `GET /auth/me`.
- [ ] `api/routes/library.py` — `GET /library/contains`, `POST /library/toggle` (both require `get_current_user`).
- [ ] Register routers + Spotify exception handlers in [backend/main.py](backend/main.py) (503 on auth/rate-limit — see migration doc item 3).

---

## 4. OAuth flow (auth-code)

```
Browser → GET /auth/spotify/login
          backend builds authorize_url(state), 302 → accounts.spotify.com
User consents → Spotify 302 → GET /auth/spotify/callback?code=…&state=…
          backend: exchange_code(code) → {access, refresh, expires}
                   fetch Spotify /me → upsert User + SpotifyAccount
                   mint our JWT → return to FE (cookie or body)
Browser → POST /library/toggle  (Authorization: Bearer <our-jwt>)
          get_current_user → load user's Spotify token (refresh if stale)
                          → follow/save on Spotify
```

State param guards CSRF; store/verify it (signed cookie or short-lived server
value — `Math.random`-free, use `secrets`).

---

## 5. Proposed API surface

```
GET  /auth/spotify/login              → 302 to Spotify consent
GET  /auth/spotify/callback?code&state → exchanges, establishes session
GET  /auth/me                          → { id, display_name } | 401
GET  /library/contains?type=&ids=      → { "<spotify_id>": bool, ... }
POST /library/toggle                   → { type, id, action, ok: true }
```

`toggle` body: `{ "type": "artist"|"album", "id": "<spotify_id>", "action": "add"|"remove" }`. `id` is the `spotify_id` already on each enriched `Artist`/`Album`. Idempotent on Spotify's side. Both `library/*` routes → 401 (not connected) rather than the old 503.

---

## 6. Spotify dashboard setup (one-time — unchanged, carried from old doc)

1. https://developer.spotify.com/dashboard → your app (the one whose ID/secret
   are in `.env`).
2. **Settings → Edit → Redirect URIs**, add exactly the backend callback, e.g.
   `http://127.0.0.1:8000/auth/spotify/callback`. Use `127.0.0.1`, **not**
   `localhost` (Spotify rejects localhost for new redirect URIs). Set
   `SPOTIFY_REDIRECT_URI` in `.env` to match exactly.
3. App can stay in **Development mode** (up to 25 manually-added users). Under
   **User Management**, list each Spotify account that will connect.

Same Client ID/Secret power reads and writes — scopes differ per flow. Write
scopes: `user-follow-read user-follow-modify user-library-read
user-library-modify`.

---

## 7. Frontend wiring (carried from old doc, adapted)

FE stays server-rendered; likes are interactive. Three pieces:

- **A "Connect Spotify" affordance** → links to the backend `/auth/spotify/login`
  (new — the old file-cache flow had no in-app login).
- **A Next route handler** proxying `POST /library/toggle` to the backend,
  forwarding the session credential, keeping `API_BASE` server-side.
- **`LikeButton` client component** — optimistic toggle, reverts on failure,
  renders nothing when `spotifyId` is null (not enriched yet).
- **Initial state in the page** — batch `GET /library/contains` server-side,
  pass `initiallyLiked` into each `ArtistTile` / `AlbumTile`.

The old doc's §4 code samples (`LikeButton.tsx`, `spotifyContains` helper, tile
wiring) still apply almost verbatim — only the proxied backend path and the
before-connect state (401 → treat all as un-liked) change. Pull them from git
history of `docs/spotify-write-access.md` if needed.

---

## 8. Open questions to settle before building

- [ ] Single-user personal vs full multi-user? (drives whether we need our-own JWT)
- [ ] Encrypt refresh tokens at rest?
- [ ] Session transport: httpOnly cookie vs bearer token in the FE.
- [ ] Where does `state` (CSRF) live — signed cookie vs server-side store?
- [ ] Do we gate *reads* behind auth too, or only writes? (currently only writes need it)

---

## 9. Suggested build order

1. User table + repo + migration (§3 Domain).
2. `SpotifyOAuth` adapter + `/auth/spotify/login` + `/callback` — get a token into the DB.
3. `core/security.py` JWT + `get_current_user` — establish a session.
4. `LibraryWritePort` + adapter + `/library/toggle` + `/contains`.
5. FE: connect button, LikeButton, initial-state batch.

Related: [functions-to-backend-migration.md](functions-to-backend-migration.md) item 1 · [alembic-setup.md](docs/alembic-setup.md)
