// Ported from the Next app; props spread out and defined locally (see
// album-tile.tsx for the rationale). Field names match the artist shape so a
// parent can do <ArtistTile {...artist} />.
export interface ArtistTileProps {
  name: string
  total_plays: number
  track_count: number
  display_name?: string | null
  top_genre?: string | null
  image_url?: string | null
  spotify_url?: string | null
  popularity?: number | null
  followers?: number | null
  spotify_genres?: string[]
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`
  return n.toString()
}

export function ArtistTile({
  name,
  total_plays,
  track_count,
  display_name = null,
  top_genre = null,
  image_url = null,
  spotify_url = null,
  popularity = null,
  followers = null,
  spotify_genres = [],
}: ArtistTileProps) {
  const cover = (
    <div className="aspect-square w-full bg-neutral-800">
      {image_url ? (
        <img
          src={image_url}
          alt={name}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-3xl text-neutral-700">
          ♪
        </div>
      )}
    </div>
  )

  return (
    <div className="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900/40 transition hover:border-neutral-700">
      {spotify_url ? (
        <a href={spotify_url} target="_blank" rel="noreferrer" title="Open in Spotify">
          {cover}
        </a>
      ) : (
        cover
      )}
      <div className="space-y-1 p-3">
        <div className="flex items-center justify-between gap-2">
          <div className="truncate font-semibold">{display_name ?? name}</div>
          {spotify_url && (
            <a
              href={spotify_url}
              target="_blank"
              rel="noreferrer"
              className="shrink-0 text-[10px] uppercase tracking-wider text-neutral-500 hover:text-green-400"
            >
              Spotify ↗
            </a>
          )}
        </div>
        <div className="flex items-center justify-between text-xs text-neutral-400">
          <span>{total_plays.toLocaleString()} plays</span>
          <span>{track_count} tracks</span>
        </div>
        {(popularity != null || followers != null) && (
          <div className="flex items-center justify-between text-xs text-neutral-500">
            {popularity != null && <span>★ {popularity}</span>}
            {followers != null && <span>{formatCount(followers)} followers</span>}
          </div>
        )}
        {top_genre && (
          <div className="truncate text-xs text-neutral-500">{top_genre}</div>
        )}
        {spotify_genres.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {spotify_genres.slice(0, 3).map((g) => (
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
  )
}
