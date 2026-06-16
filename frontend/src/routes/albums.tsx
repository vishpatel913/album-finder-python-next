import { useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { useMemo, useState } from 'react'
import { albumsQuery } from '@/lib/queries'

export function AlbumsPage() {
  const { data, isLoading, error } = useQuery(albumsQuery())
  const [search, setSearch] = useState('')

  // Client-side filter for now; swap for a backend search endpoint later by
  // moving this into the queryKey + queryFn.
  const albums = useMemo(() => {
    if (!data) return []
    const q = search.trim().toLowerCase()
    if (!q) return data
    return data.filter(
      (a) => a.name.toLowerCase().includes(q) || a.genre.toLowerCase().includes(q),
    )
  }, [data, search])

  if (isLoading) return <p className="text-zinc-400">Loading library…</p>
  if (error) return <p className="text-red-400">{(error as Error).message}</p>

  return (
    <div className="space-y-4">
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Filter by name or genre…"
        className="w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:border-brand focus:outline-none"
      />

      <ul className="divide-y divide-zinc-800 rounded-lg border border-zinc-800">
        {albums.map((album) => (
          <li key={album.id}>
            <Link
              to="/album/$albumId"
              params={{ albumId: album.id }}
              className="flex items-center justify-between px-4 py-3 hover:bg-zinc-900"
            >
              <span className="font-medium text-zinc-100">{album.name}</span>
              <span className="text-sm text-zinc-400">
                {album.genre} · {album.year}
              </span>
            </Link>
          </li>
        ))}
        {albums.length === 0 && (
          <li className="px-4 py-6 text-center text-zinc-500">No albums match.</li>
        )}
      </ul>
    </div>
  )
}
