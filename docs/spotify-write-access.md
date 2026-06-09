# Spotify write access — follow artists, save albums

Adds user-authorised "like" actions on top of the read-only enrichment.
"Like" maps to: **artist → follow**, **album → save**. (Tracks are out of
scope — `TrackRow` has no Spotify ID yet.)

The **backend is done**. This doc covers (1) the one-time setup you run on your
machine, and (2) how to wire the frontend.

---

## 1. Spotify dashboard setup (one-time)

1. Open https://developer.spotify.com/dashboard and select your app (the one
   whose ID/secret are already in `.env`).
2. **Settings → Edit → Redirect URIs**, add exactly:
   ```
   http://127.0.0.1:8888/callback
   ```
   Use `127.0.0.1`, **not** `localhost` (Spotify rejects localhost for new
   redirect URIs). Save.
3. The app can stay in **Development mode** (allows up to 25 manually-added
   users — no quota extension needed for personal use). Under **User
   Management**, make sure your own Spotify account is listed.

Same Client ID/Secret power both read enrichment and writes — nothing else to
change there.

## 2. One-time consent

On a machine with a browser, from the repo root:

```bash
functions/venv/bin/python scripts/spotify_authorize.py
```

This opens the consent page, captures the redirect, and writes
`data/.spotify-user-token-cache`. After this, the API auto-refreshes the token
forever — no browser needed again.

**Docker:** important — `/app/data` is a **named volume** (`album-finder-data`),
not a bind-mount of `./data`. Running the script on the host writes the token to
the repo's `./data/`, which the container does **not** see. Seed the volume once:

```bash
functions/venv/bin/python scripts/spotify_authorize.py            # on the host (needs a browser)
docker compose up -d api
docker compose cp ./data/.spotify-user-token-cache api:/app/data/.spotify-user-token-cache
```

Writing to the mounted path persists to the volume and survives restarts /
`compose down`. spotipy refreshes the token in place, so this copy is one-time.
No restart needed (the failed first call caches nothing), but restarting `api`
is harmless.

**Other bare-metal machines:** just copy `data/.spotify-user-token-cache` across
(it's gitignored, never committed).

Optional override: set `SPOTIFY_REDIRECT_URI` in `.env` if you registered a
different URI (must match the dashboard exactly).

---

## 3. Backend API reference

Both endpoints use the user token and return **503** with a `detail` message
until consent has been run — surface that to the user as "connect Spotify".

### `GET /api/spotify/library/contains`
Initial like-state for a set of entities, so buttons render filled correctly.

| Param | |
|---|---|
| `type` | `artist` \| `album` |
| `ids` | comma-separated Spotify IDs |

Response: `{ "<spotify_id>": true, ... }` (only the IDs you asked for).

```
GET /api/spotify/library/contains?type=artist&ids=66CXWj,1dfeR4
→ { "66CXWj": true, "1dfeR4": false }
```

### `POST /api/spotify/library/toggle`
Follow/unfollow an artist or save/remove an album.

```jsonc
// body
{ "type": "artist", "id": "66CXWj...", "action": "add" }   // or "album" / "remove"
// → { "type": "artist", "id": "66CXWj...", "action": "add", "ok": true }
```

`id` is the `spotify_id` already on each enriched `Artist`/`Album`. Idempotent
on Spotify's side (re-adding/removing is harmless).

---

## 4. Frontend wiring

The current app fetches entirely server-side. Like buttons are interactive, so
you need three small pieces.

### 4a. Route handlers (keep `API_BASE` server-side)

Create `app/api/spotify/toggle/route.ts`:

```ts
import { NextResponse } from "next/server";

const API_BASE = process.env.API_BASE ?? "http://localhost:8000";

export async function POST(req: Request) {
  const body = await req.json();
  const res = await fetch(`${API_BASE}/api/spotify/library/toggle`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  return NextResponse.json(await res.json(), { status: res.status });
}
```

(You only strictly need `toggle` from the client. `contains` is better called
server-side in the page — see 4c.)

### 4b. `LikeButton` client component

`app/components/LikeButton.tsx`:

```tsx
"use client";
import { useState } from "react";

type Props = {
  type: "artist" | "album";
  spotifyId: string | null;
  initiallyLiked: boolean;
};

export function LikeButton({ type, spotifyId, initiallyLiked }: Props) {
  const [liked, setLiked] = useState(initiallyLiked);
  const [busy, setBusy] = useState(false);
  if (!spotifyId) return null; // not enriched yet — nothing to like

  async function toggle() {
    const next = !liked;
    setLiked(next); // optimistic
    setBusy(true);
    try {
      const res = await fetch("/api/spotify/toggle", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          type,
          id: spotifyId,
          action: next ? "add" : "remove",
        }),
      });
      if (!res.ok) throw new Error(String(res.status));
    } catch {
      setLiked(!next); // revert on failure
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      onClick={toggle}
      disabled={busy}
      aria-pressed={liked}
      title={type === "artist" ? "Follow on Spotify" : "Save on Spotify"}
      className={`shrink-0 text-sm transition ${
        liked ? "text-green-400" : "text-neutral-500 hover:text-green-400"
      } disabled:opacity-50`}
    >
      {liked ? "♥" : "♡"}
    </button>
  );
}
```

### 4c. Fetch initial state in the page, pass down

In `app/artists/page.tsx` (server component), after fetching the artists, batch
the contains check and pass `initiallyLiked` into each tile. Add a helper to
`app/lib/api.ts`:

```ts
// in app/lib/api.ts
export async function spotifyContains(
  type: "artist" | "album",
  ids: string[],
): Promise<Record<string, boolean>> {
  const valid = ids.filter(Boolean);
  if (valid.length === 0) return {};
  try {
    return await fetchJson<Record<string, boolean>>(
      "/api/spotify/library/contains",
      { type, ids: valid.join(",") },
    );
  } catch {
    return {}; // 503 before consent → render everything un-liked
  }
}
```

Then in the page:

```tsx
const artists = await api.artists(params);
const likeMap = await spotifyContains(
  "artist",
  artists.map((a) => a.spotify_id).filter((x): x is string => !!x),
);
// ...
{artists.map((a) => (
  <ArtistTile
    key={a.name}
    artist={a}
    initiallyLiked={a.spotify_id ? likeMap[a.spotify_id] ?? false : false}
  />
))}
```

### 4d. Drop the button into the tile

In `app/components/ArtistTile.tsx`, take the new prop and render the button in
the header row next to the name (alongside the existing "Spotify ↗" link):

```tsx
export function ArtistTile({
  artist,
  initiallyLiked,
}: {
  artist: Artist;
  initiallyLiked: boolean;
}) {
  // ...
  // in the flex header row:
  <LikeButton type="artist" spotifyId={artist.spotify_id} initiallyLiked={initiallyLiked} />
}
```

Repeat for `AlbumTile.tsx` with `type="album"` and `spotifyContains("album", …)`
in `app/albums/page.tsx`.

---

## Notes / gotchas

- **Before consent**, every write endpoint returns 503. The `spotifyContains`
  helper swallows that to `{}` so the UI still renders (all un-liked); `toggle`
  failures revert the optimistic state. Consider a one-line banner if you want
  to prompt "run the authorize script".
- **`contains` ID caps**: 50 (artist) / 20 (album) per Spotify request — the
  backend already chunks, so pass as many IDs as you like.
- **Tracks**: would need a track resolver to obtain Spotify track IDs first.
  Not built. Endpoints are artist/album only.
