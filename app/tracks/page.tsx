import { Filters } from "@/app/components/Filters";
import { TrackRow } from "@/app/components/TrackRow";
import { api } from "@/app/lib/api";

type SearchParams = { [key: string]: string | string[] | undefined };

function pick(params: SearchParams, key: string): string | undefined {
  const v = params[key];
  return Array.isArray(v) ? v[0] : v;
}

export default async function TracksPage({ searchParams }: { searchParams: SearchParams }) {
  const filterParams = {
    limit: pick(searchParams, "limit") ?? 100,
    min_plays: pick(searchParams, "min_plays") ?? 1,
    artist: pick(searchParams, "artist"),
    q: pick(searchParams, "q"),
    genre: pick(searchParams, "genre"),
    year: pick(searchParams, "year"),
    year_from: pick(searchParams, "year_from"),
    year_to: pick(searchParams, "year_to"),
    added_after: pick(searchParams, "added_after"),
    min_rating: pick(searchParams, "min_rating"),
    loved: pick(searchParams, "loved"),
    sort: pick(searchParams, "sort") ?? "plays_desc",
  };

  let tracks: Awaited<ReturnType<typeof api.tracks>> = [];
  let facets: Awaited<ReturnType<typeof api.facets>> | null = null;
  let error: string | null = null;
  try {
    [tracks, facets] = await Promise.all([api.tracks(filterParams), api.facets()]);
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  const genreOptions = (facets?.genres ?? []).map((g) => ({ value: g, label: g }));

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Top tracks</h1>
        <p className="text-sm text-neutral-400">{tracks.length} shown</p>
      </div>

      <Filters
        fields={[
          { name: "q", label: "Search", type: "text", placeholder: "title contains…" },
          { name: "artist", label: "Artist (exact)", type: "text" },
          { name: "genre", label: "Genre", type: "select", options: genreOptions },
          { name: "year", label: "Year", type: "number" },
          { name: "year_from", label: "Year from", type: "number" },
          { name: "year_to", label: "Year to", type: "number" },
          { name: "added_after", label: "Added after", type: "date" },
          { name: "min_plays", label: "Min plays", type: "number" },
          { name: "min_rating", label: "Min rating (0–100)", type: "number" },
          { name: "loved", label: "Loved only", type: "checkbox" },
          {
            name: "sort",
            label: "Sort",
            type: "select",
            options: [
              { value: "plays_desc", label: "Plays ↓" },
              { value: "plays_asc", label: "Plays ↑" },
              { value: "added_desc", label: "Recently added" },
              { value: "added_asc", label: "Earliest added" },
              { value: "rating_desc", label: "Rating ↓" },
              { value: "last_played_desc", label: "Recently played" },
              { value: "name", label: "Name A–Z" },
            ],
          },
          { name: "limit", label: "Limit", type: "number" },
        ]}
      />

      {error && (
        <div className="rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      {!error && tracks.length === 0 && (
        <div className="rounded-lg border border-neutral-800 p-8 text-center text-neutral-500">
          No tracks match these filters.
        </div>
      )}

      {tracks.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-neutral-800">
          <table className="min-w-full text-sm">
            <thead className="bg-neutral-900 text-left text-xs uppercase tracking-wider text-neutral-500">
              <tr>
                <th className="px-3 py-2">Title</th>
                <th className="px-3 py-2">Artist</th>
                <th className="px-3 py-2">Album</th>
                <th className="px-3 py-2">Genre</th>
                <th className="px-3 py-2 text-right">Plays</th>
                <th className="px-3 py-2 text-right">Year</th>
                <th className="px-3 py-2 text-right">Rating</th>
                <th className="px-3 py-2 text-right">Added</th>
              </tr>
            </thead>
            <tbody>
              {tracks.map((t, idx) => (
                <TrackRow key={`${t.artist}-${t.name}-${idx}`} track={t} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
