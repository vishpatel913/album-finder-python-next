import type { Artist } from "@/app/lib/api";

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return n.toString();
}

export function ArtistTile({ artist }: { artist: Artist }) {
  const cover = (
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
  );

  return (
    <div className="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900/40 transition hover:border-neutral-700">
      {artist.spotify_url ? (
        <a href={artist.spotify_url} target="_blank" rel="noreferrer" title="Open in Spotify">
          {cover}
        </a>
      ) : (
        cover
      )}
      <div className="space-y-1 p-3">
        <div className="flex items-center justify-between gap-2">
          <div className="truncate font-semibold">{artist.display_name ?? artist.name}</div>
          {artist.spotify_url && (
            <a
              href={artist.spotify_url}
              target="_blank"
              rel="noreferrer"
              className="shrink-0 text-[10px] uppercase tracking-wider text-neutral-500 hover:text-green-400"
            >
              Spotify ↗
            </a>
          )}
        </div>
        <div className="flex items-center justify-between text-xs text-neutral-400">
          <span>{artist.total_plays.toLocaleString()} plays</span>
          <span>{artist.track_count} tracks</span>
        </div>
        {(artist.popularity != null || artist.followers != null) && (
          <div className="flex items-center justify-between text-xs text-neutral-500">
            {artist.popularity != null && <span>★ {artist.popularity}</span>}
            {artist.followers != null && <span>{formatCount(artist.followers)} followers</span>}
          </div>
        )}
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
