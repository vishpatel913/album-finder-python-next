// MSW handlers typed against the generated OpenAPI `paths`. openapi-msw
// enforces that each path exists, params are correct, and `response(200)`
// bodies match the spec — so a regenerated api.gen.ts breaks the build here
// instead of silently drifting from the backend.
import { HttpResponse } from 'msw'
import { createOpenApiHttp } from 'openapi-msw'
import type { paths } from '@/types/api.gen'
import { db } from './db'
import { spotifyTrack } from './factories'

// The app fetches via the /api prefix (normally stripped by the Vite proxy);
// the service worker sees the un-rewritten URL, hence the baseUrl.
const http = createOpenApiHttp<paths>({ baseUrl: '/api' })

const notFound = (detail: string) =>
  HttpResponse.json({ detail }, { status: 404 })

const byName =
  (q: string) =>
  <T extends { name: string | null }>(item: T) =>
    item.name?.toLowerCase().includes(q.toLowerCase()) ?? false

export const handlers = [
  http.get('/health', ({ response }) => response(200).json({ status: 'ok' })),
  http.get('/health/ready', ({ response }) =>
    response(200).json({ status: 'ready' }),
  ),

  // Library: artists
  http.get('/artist/', ({ response }) =>
    response(200).json(
      db.artists.map((a) => db.artistWithAlbums(a.id)!),
    ),
  ),
  http.get('/artist/{artist_id}', ({ params, response }) => {
    const artist = db.artistWithAlbums(params.artist_id)
    if (!artist) return response.untyped(notFound('Artist not found'))
    return response(200).json(artist)
  }),
  http.post('/artist/{artist_id}/enrich', ({ params, response }) =>
    response(200).json(db.artists.find((a) => a.id === params.artist_id) ?? null),
  ),

  // Library: albums
  http.get('/album/', ({ response }) => response(200).json(db.albums)),
  http.get('/album/{album_id}', ({ params, response }) => {
    const album = db.albums.find((a) => a.id === params.album_id)
    if (!album) return response.untyped(notFound('Album not found'))
    return response(200).json(album)
  }),
  http.post('/album/{album_id}/enrich', ({ params, response }) =>
    response(200).json(db.albums.find((a) => a.id === params.album_id) ?? null),
  ),

  // Library: tracks
  http.get('/track/', ({ response }) => response(200).json(db.tracks)),
  http.get('/track/{track_id}', ({ params, response }) => {
    const track = db.tracks.find((t) => t.id === params.track_id)
    if (!track) return response.untyped(notFound('Track not found'))
    return response(200).json(track)
  }),

  // Spotify search
  http.get('/search/album', ({ query, response }) =>
    response(200).json(db.spotify.albums.filter(byName(query.get('q')))),
  ),
  http.get('/search/album/{album_id}', ({ params, response }) => {
    const album = db.spotify.albums.find((a) => a.id === params.album_id)
    if (!album) return response.untyped(notFound('Album not found'))
    return response(200).json(album)
  }),
  http.get('/search/album/{album_id}/tracks', ({ params, response }) => {
    const album = db.spotify.albums.find((a) => a.id === params.album_id)
    if (!album) return response.untyped(notFound('Album not found'))
    const tracks = Array.from({ length: album.total_tracks ?? 10 }, (_, i) =>
      spotifyTrack({ album, artists: album.artists, track_number: i + 1 }),
    )
    return response(200).json(tracks)
  }),
  http.get('/search/artist', ({ query, response }) =>
    response(200).json(db.spotify.artists.filter(byName(query.get('q')))),
  ),
  http.get('/search/artist/{artist_id}', ({ params, response }) => {
    const artist = db.spotify.artists.find((a) => a.id === params.artist_id)
    if (!artist) return response.untyped(notFound('Artist not found'))
    return response(200).json(artist)
  }),
  http.get('/search/artist/{artist_id}/albums', ({ params, response }) =>
    response(200).json(
      db.spotify.albums.filter((a) =>
        a.artists.some((ar) => ar.id === params.artist_id),
      ),
    ),
  ),
]
