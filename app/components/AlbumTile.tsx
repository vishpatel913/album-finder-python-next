import type { Album } from "@/app/lib/api";

export function AlbumTile({ album }: { album: Album }) {
  const cover = (
    <div className="aspect-square w-full bg-neutral-800">
      {album.image_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={album.image_url}
          alt={album.album}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-3xl text-neutral-700">
          ♫
        </div>
      )}
    </div>
  );

  // Prefer Spotify's release year if enriched, else the library's.
  const year = album.release_date?.slice(0, 4) ?? (album.year ? String(album.year) : null);

  return (
    <div className="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900/40 transition hover:border-neutral-700">
      {album.spotify_url ? (
        <a href={album.spotify_url} target="_blank" rel="noreferrer" title="Open in Spotify">
          {cover}
        </a>
      ) : (
        cover
      )}
      <div className="space-y-1 p-3">
        <div className="flex items-center justify-between gap-2">
          <div className="truncate font-semibold" title={album.album}>
            {album.album}
          </div>
          {album.spotify_url && (
            <a
              href={album.spotify_url}
              target="_blank"
              rel="noreferrer"
              className="shrink-0 text-[10px] uppercase tracking-wider text-neutral-500 hover:text-green-400"
            >
              Spotify ↗
            </a>
          )}
        </div>
        <div className="truncate text-sm text-neutral-400" title={album.artist}>
          {album.artist}
        </div>
        <div className="flex items-center justify-between text-xs text-neutral-500">
          <span>{album.total_plays.toLocaleString()} plays</span>
          <span>
            {album.track_count} tracks{year ? ` · ${year}` : ""}
          </span>
        </div>
        {album.top_genre && (
          <div className="truncate text-xs text-neutral-500">{album.top_genre}</div>
        )}
      </div>
    </div>
  );
}
