import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "@tanstack/react-router";
import { artistQuery } from "@/lib/queries";

export function ArtistDetailPage() {
  const { artistId } = useParams({ from: "/artist/$artistId" });
  const { data: artist, isLoading, error } = useQuery(artistQuery(artistId));

  if (isLoading) return <p className="text-zinc-400">Loading…</p>;
  if (error) return <p className="text-red-400">{(error as Error).message}</p>;
  if (!artist) return null;

  return (
    <div className="space-y-6">
      <Link to="/artists" className="text-sm text-brand hover:underline">
        ← Back to library
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100">
            {artist.name}
          </h1>
          <p className="mt-1 text-zinc-400"></p>
        </div>
      </div>
    </div>
  );
}
