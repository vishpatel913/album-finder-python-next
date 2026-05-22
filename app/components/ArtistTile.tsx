import type { Artist } from "@/app/lib/api";

export function ArtistTile({ artist }: { artist: Artist }) {
  return (
    <div className="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900/40 transition hover:border-neutral-700">
      <div className="aspect-square w-full bg-neutral-800">
        {artist.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={artist.image_url}
            alt={artist.name}
            className="h-full w-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-3xl text-neutral-700">
            ♪
          </div>
        )}
      </div>
      <div className="space-y-1 p-3">
        <div className="truncate font-semibold">{artist.display_name ?? artist.name}</div>
        <div className="flex items-center justify-between text-xs text-neutral-400">
          <span>{artist.total_plays.toLocaleString()} plays</span>
          <span>{artist.track_count} tracks</span>
        </div>
        {artist.top_genre && (
          <div className="truncate text-xs text-neutral-500">{artist.top_genre}</div>
        )}
        {artist.spotify_genres.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {artist.spotify_genres.slice(0, 3).map((g) => (
              <span
                key={g}
                className="rounded-full bg-neutral-800 px-2 py-0.5 text-[10px] text-neutral-300"
              >
                {g}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
