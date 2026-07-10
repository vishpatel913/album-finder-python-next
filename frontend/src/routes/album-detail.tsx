import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "@tanstack/react-router";
import { albumQuery } from "@/lib/queries";

export function AlbumDetailPage() {
  // `from` ties the params to the route path for full type-safety.
  const { albumId } = useParams({ from: "/album/$albumId" });
  const { data: album, isLoading, error } = useQuery(albumQuery(albumId));

  if (isLoading) return <p className="text-zinc-400">Loading…</p>;
  if (error) return <p className="text-red-400">{(error as Error).message}</p>;
  if (!album) return null;

  return (
    <div className="space-y-6">
      <Link to="/albums" className="text-sm text-brand hover:underline">
        ← Back to library
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100">{album.name}</h1>
          <p className="mt-1 text-zinc-400">
            {album.genre} · {album.year}
            {album.is_compilation && " · Compilation"}
          </p>
        </div>
      </div>
    </div>
  );
}
