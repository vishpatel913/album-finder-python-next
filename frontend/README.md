# Album Finder — Frontend

Vite + React 19 + TypeScript SPA for the FastAPI backend.

- **TanStack Query** — server-state cache (reads, mutations, invalidation)
- **TanStack Router** — type-safe, code-based routing (`src/router.tsx`)
- **Tailwind v4** — CSS-first config via the Vite plugin (no `tailwind.config.js`)
- **Radix primitives** — accessible, unstyled UI, styled with Tailwind

## Run locally (host)

The backend must be up (`docker compose up api database`), exposed on `:8004`.

```bash
npm install
npm run dev        # http://localhost:5173
```

The dev server proxies `/api/*` → `http://localhost:8004` (see `vite.config.ts`),
so there's no CORS to configure. Override the target with `VITE_PROXY_TARGET`.

## Run in Docker (compose)

```bash
docker compose up web        # brings up api + database too
```

In compose, `VITE_PROXY_TARGET=http://api:8000` points the proxy at the `api`
service over the compose network.

## Structure

```
src/
  lib/
    api.ts            fetch wrapper (everything relative to /api)
    queries.ts        query options, keys, and mutation hooks
    query-client.ts   QueryClient defaults
  routes/             one component per page
  components/         UI (Radix + Tailwind)
  router.tsx          route tree
  types/index.ts      mirrors backend *Read schemas
```

## API types (generated)

Entity types come from the backend's OpenAPI doc, so they can't drift:

```bash
npm run gen:api     # backend must be up on :8004
```

This writes `src/types/api.gen.ts` (committed, so the app typechecks without a
running backend). `src/types/index.ts` re-exports clean aliases from it:

```ts
import type { components } from './api.gen'
export type Album = components['schemas']['AlbumRead']
```

Regenerate whenever the backend's request/response models change. `Track` is
still hand-defined — the backend has no `TrackRead` response model yet.

## Notes

- The edit dialog calls `PUT /album/{id}`, which the backend doesn't expose yet.
  The hook is wired — it'll work the moment that route lands.
- Ported tiles (`album-tile`, `artist-tile`, `track-row`) use a Spotify-enriched
  shape the current backend doesn't fully serve. Their props are spread out and
  defined locally, so they compile independently; pass `{...album}` once the data
  is there.
