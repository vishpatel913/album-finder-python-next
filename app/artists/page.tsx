import { Filters } from "@/app/components/Filters";
import { ArtistTile } from "@/app/components/ArtistTile";
import { api } from "@/app/lib/api";

type SearchParams = { [key: string]: string | string[] | undefined };

function pick(params: SearchParams, key: string): string | undefined {
  const v = params[key];
  return Array.isArray(v) ? v[0] : v;
}

export default async function ArtistsPage({ searchParams }: { searchParams: SearchParams }) {
  const filterParams = {
    limit: pick(searchParams, "limit") ?? 50,
    min_plays: pick(searchParams, "min_plays") ?? 5,
    q: pick(searchParams, "q"),
    genre: pick(searchParams, "genre"),
    vibe: pick(searchParams, "vibe"),
    year_from: pick(searchParams, "year_from"),
    year_to: pick(searchParams, "year_to"),
    added_after: pick(searchParams, "added_after"),
    sort: pick(searchParams, "sort") ?? "plays_desc",
  };

  let artists: Awaited<ReturnType<typeof api.artists>> = [];
  let facets: Awaited<ReturnType<typeof api.facets>> | null = null;
  let error: string | null = null;
  try {
    [artists, facets] = await Promise.all([api.artists(filterParams), api.facets()]);
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  const genreOptions = (facets?.genres ?? []).map((g) => ({ value: g, label: g }));

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Top artists</h1>
          <p className="text-sm text-neutral-400">
            {facets ? `${facets.total_artists} parsed · ${facets.total_tracks} tracks` : ""}
          </p>
        </div>
      </div>

      <Filters
        fields={[
          { name: "q", label: "Search", type: "text", placeholder: "name contains…" },
          { name: "genre", label: "Genre (Music.app)", type: "select", options: genreOptions },
          { name: "vibe", label: "Vibe (Spotify)", type: "text", placeholder: "shoegaze, lo-fi…" },
          { name: "min_plays", label: "Min plays", type: "number" },
          { name: "year_from", label: "Year from", type: "number" },
          { name: "year_to", label: "Year to", type: "number" },
          { name: "added_after", label: "Added after", type: "date" },
          {
            name: "sort",
            label: "Sort",
            type: "select",
            options: [
              { value: "plays_desc", label: "Plays ↓" },
              { value: "plays_asc", label: "Plays ↑" },
              { value: "name", label: "Name A–Z" },
              { value: "added_desc", label: "Recently added" },
              { value: "added_asc", label: "Earliest added" },
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

      {!error && artists.length === 0 && (
        <div className="rounded-lg border border-neutral-800 p-8 text-center text-neutral-500">
          No artists match these filters.
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {artists.map((a) => (
          <ArtistTile key={a.name} artist={a} />
        ))}
      </div>
    </div>
  );
}
