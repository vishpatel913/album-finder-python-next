// Ported from the Next app. Props are spread out and defined locally so this
// component is decoupled from any shared API type. Field names match the
// (Spotify-enriched) album shape, so a parent can do <AlbumTile {...album} />.
// NOTE: the current backend AlbumRead doesn't serve image_url / plays / spotify
// fields yet — they're optional here, ready for when enrichment lands.
export interface AlbumTileProps {
  /** Album title. */
  album: string
  artist: string
  total_plays: number
  track_count: number
  top_genre?: string | null
  year?: number | null
  image_url?: string | null
  spotify_url?: string | null
  /** Spotify release date (ISO); its year wins over `year` when present. */
  release_date?: string | null
}

export function AlbumTile({
  album,
  artist,
  total_plays,
  track_count,
  top_genre = null,
  year = null,
  image_url = null,
  spotify_url = null,
  release_date = null,
}: AlbumTileProps) {
  const cover = (
    <div className="aspect-square w-full bg-neutral-800">
      {image_url ? (
        <img
          src={image_url}
          alt={album}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-3xl text-neutral-700">
          ♫
        </div>
      )}
    </div>
  )

  // Prefer Spotify's release year if enriched, else the library's.
  const displayYear = release_date?.slice(0, 4) ?? (year ? String(year) : null)

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
          <div className="truncate font-semibold" title={album}>
            {album}
          </div>
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
        <div className="truncate text-sm text-neutral-400" title={artist}>
          {artist}
        </div>
        <div className="flex items-center justify-between text-xs text-neutral-500">
          <span>{total_plays.toLocaleString()} plays</span>
          <span>
            {track_count} tracks{displayYear ? ` · ${displayYear}` : ''}
          </span>
        </div>
        {top_genre && (
          <div className="truncate text-xs text-neutral-500">{top_genre}</div>
        )}
      </div>
    </div>
  )
}
