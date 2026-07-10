import React from "react";
import { Placeholder } from "./ui/placeholder";

export interface AlbumTileProps {
  /** Album title. */
  name: string;
  artist?: string | null;
  year?: number | null;
  genre?: string | null;
  trackCount?: number | null;
  imageUrl?: string | null;
  /** Spotify release date (ISO); its year wins over `year` when present. */
  releaseDate?: string | null;
  actions?: React.ReactNode | null;
}

export function AlbumTile({
  name,
  artist = null,
  year = null,
  genre = null,
  trackCount = null,
  imageUrl = null,
  releaseDate = null,
  actions = null,
}: AlbumTileProps) {
  // Prefer Spotify's release year if enriched, else the library's.
  const displayYear = releaseDate?.slice(0, 4) ?? (year ? String(year) : null);

  return (
    <div className="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900/40 transition hover:border-neutral-700">
      <div className="relative">
        <div className="absolute w-full flex justify-end p-2">{actions}</div>
        <div className="aspect-square w-full bg-neutral-800">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={name}
              className="h-full w-full object-cover"
              loading="lazy"
            />
          ) : (
            <Placeholder />
          )}
        </div>
      </div>
      <div className="space-y-1 p-3">
        <div className="truncate font-semibold" title={name}>
          {name}
        </div>
        <div className="truncate text-sm text-neutral-400" title={artist ?? ""}>
          {artist}
        </div>
        <div className="flex items-center justify-between text-xs text-neutral-500">
          {displayYear ? <span>{displayYear}</span> : null}
        </div>
        {genre && (
          <div className="truncate text-xs text-neutral-500">{genre}</div>
        )}
      </div>
    </div>
  );
}
