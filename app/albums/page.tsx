import { Filters } from "@/app/components/Filters";
import { AlbumTile } from "@/app/components/AlbumTile";
import { api } from "@/app/lib/api";

type SearchParams = { [key: string]: string | string[] | undefined };

function pick(params: SearchParams, key: string): string | undefined {
  const v = params[key];
  return Array.isArray(v) ? v[0] : v;
}

export default async function AlbumsPage({ searchParams }: { searchParams: SearchParams }) {
  const filterParams = {
    limit: pick(searchParams, "limit") ?? 100,
    min_plays: pick(searchParams, "min_plays") ?? 0,
    q: pick(searchParams, "q"),
    artist: pick(searchParams, "artist"),
    genre: pick(searchParams, "genre"),
    year_from: pick(searchParams, "year_from"),
    year_to: pick(searchParams, "year_to"),
    added_after: pick(searchParams, "added_after"),
    include_greatest_hits: pick(searchParams, "include_greatest_hits"),
    sort: pick(searchParams, "sort") ?? "plays_desc",
  };

  let albums: Awaited<ReturnType<typeof api.albums>> = [];
  let facets: Awaited<ReturnType<typeof api.facets>> | null = null;
  let error: string | null = null;
  try {
    [albums, facets] = await Promise.all([api.albums(filterParams), api.facets()]);
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  const genreOptions = (facets?.genres ?? []).map((g) => ({ value: g, label: g }));

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Albums</h1>
          <p className="text-sm text-neutral-400">
            {albums.length} shown · compilations hidden
          </p>
        </div>
      </div>

      <Filters
        fields={[
          { name: "q", label: "Search", type: "text", placeholder: "album contains…" },
          { name: "artist", label: "Artist (exact)", type: "text" },
          { name: "genre", label: "Genre (Music.app)", type: "select", options: genreOptions },
          { name: "year_from", label: "Year from", type: "number" },
          { name: "year_to", label: "Year to", type: "number" },
          { name: "added_after", label: "Added after", type: "date" },
          { name: "min_plays", label: "Min plays", type: "number" },
          { name: "include_greatest_hits", label: "Greatest hits", type: "checkbox" },
          {
            name: "sort",
            label: "Sort",
            type: "select",
            options: [
              { value: "plays_desc", label: "Plays ↓" },
              { value: "plays_asc", label: "Plays ↑" },
              { value: "year_desc", label: "Newest" },
              { value: "year_asc", label: "Oldest" },
              { value: "added_desc", label: "Recently added" },
              { value: "added_asc", label: "Earliest added" },
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

      {!error && albums.length === 0 && (
        <div className="rounded-lg border border-neutral-800 p-8 text-center text-neutral-500">
          No albums match these filters.
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {albums.map((a) => (
          <AlbumTile key={`${a.artist}-${a.album}`} album={a} />
        ))}
      </div>
    </div>
  );
}
