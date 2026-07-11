import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { albumsQuery } from "@/lib/queries";
import { AlbumTile } from "@/components/album-tile";
import { SpotifyEnrichButton } from "@/components/spotify-enrich";

export function AlbumsPage() {
  const { data, isLoading, error } = useQuery(albumsQuery());
  const [search, setSearch] = useState("");

  // Client-side filter for now; swap for a backend search endpoint later by
  // moving this into the queryKey + queryFn.
  const albums = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data;
    return data.filter((a) => a.name.toLowerCase().includes(q));
  }, [data, search]);

  if (isLoading) return <p className="text-zinc-400">Loading library…</p>;
  if (error) return <p className="text-red-400">{(error as Error).message}</p>;

  return (
    <div className="space-y-4">
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Filter by name or genre…"
        className="w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:border-brand focus:outline-none"
      />

      <ul className="grid grid-cols-5 w-full gap-4">
        {albums.map((album) => (
          <AlbumTile
            name={album.name}
            artist={album.artist?.name}
            year={album.year}
            genre={album.genre}
            imageUrl={album.artwork_url}
            releaseDate={String(album.year)}
            actions={
              <SpotifyEnrichButton
                type="album"
                id={album.id}
                spotifyId={album.spotify_id}
              />
            }
          />
        ))}
        {albums.length === 0 && (
          <li className="px-4 py-6 text-center text-zinc-500">
            No albums match.
          </li>
        )}
      </ul>
    </div>
  );
}
