// Server-side API client for the FastAPI sidecar.
// Reads API_BASE from env so docker-compose can override it (api:8000)
// while local bare-metal dev uses http://localhost:8000.

const API_BASE = process.env.API_BASE ?? "http://localhost:8000";

export type Artist = {
  name: string;
  total_plays: number;
  track_count: number;
  top_genre: string | null;
  all_genres: string[];
  year_min: number | null;
  year_max: number | null;
  date_added_first: string | null;
  date_added_last: string | null;
  avg_rating: number | null;
  loved_count: number;
  spotify_id: string | null;
  display_name: string | null;
  image_url: string | null;
  spotify_genres: string[];
};

export type TrackRow = {
  artist: string;
  name: string;
  album: string;
  genre: string;
  year: number | null;
  plays: number;
  rating: number | null;
  loved: boolean;
  date_added: string | null;
  last_played: string | null;
};

export type Facets = {
  genres: string[];
  year_min: number | null;
  year_max: number | null;
  total_artists: number;
  total_tracks: number;
};

export type Health = {
  library_path: string;
  library_mtime: string | null;
  artists_parsed: number;
  cache_entries: number;
};

export type DuplicateGroup = { names: string[] };

type SearchParams = Record<string, string | number | boolean | undefined | null>;

function toQuery(params: SearchParams): string {
  const usp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    usp.set(key, String(value));
  }
  const q = usp.toString();
  return q ? `?${q}` : "";
}

async function fetchJson<T>(path: string, params: SearchParams = {}): Promise<T> {
  const url = `${API_BASE}${path}${toQuery(params)}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API ${res.status} ${res.statusText} for ${url}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => fetchJson<Health>("/api/health"),
  artists: (params: SearchParams = {}) => fetchJson<Artist[]>("/api/library/artists", params),
  tracks: (params: SearchParams = {}) => fetchJson<TrackRow[]>("/api/library/tracks", params),
  facets: () => fetchJson<Facets>("/api/library/facets"),
  duplicates: () => fetchJson<DuplicateGroup[]>("/api/library/duplicates"),
};
