import Link from "next/link";
import { api } from "@/app/lib/api";
import { Button } from "@/app/components/ui/button";

export default async function Home() {
  let health: Awaited<ReturnType<typeof api.health>> | null = null;
  let dupes: Awaited<ReturnType<typeof api.duplicates>> = [];
  let error: string | null = null;

  try {
    [health, dupes] = await Promise.all([api.health(), api.duplicates().catch(() => [])]);
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold tracking-tight">Your library</h1>
        <p className="mt-2 text-neutral-400">
          Ranked from your Music.app export. Hit /artists or /tracks to browse.
        </p>
      </section>

      {error && (
        <div className="rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm">
          <p className="font-semibold text-red-300">API unreachable</p>
          <p className="mt-1 text-red-200/80">{error}</p>
          <p className="mt-2 text-red-200/60">
            Is the FastAPI service running? Try <code>docker compose up</code> or run uvicorn
            directly from <code>functions/</code>.
          </p>
        </div>
      )}

      {health && (
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Stat label="Artists" value={health.artists_parsed.toString()} />
          <Stat label="Cache entries" value={health.cache_entries.toString()} />
          <Stat label="Library mtime" value={health.library_mtime ?? "—"} />
          <Stat label="Library path" value={health.library_path} mono />
        </section>
      )}

      {dupes.length > 0 && (
        <section className="rounded-lg border border-amber-900 bg-amber-950/30 p-4">
          <p className="font-semibold text-amber-200">
            Near-duplicate Album Artists ({dupes.length})
          </p>
          <p className="mt-1 text-sm text-amber-200/70">
            Clean these up in Music.app for consistent grouping.
          </p>
          <ul className="mt-3 space-y-1 text-sm">
            {dupes.map((group, idx) => (
              <li key={idx} className="text-amber-100/90">
                {group.names.join("  |  ")}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="flex gap-4">
        <Button asChild variant="primary">
          <Link href="/artists">Browse artists →</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/tracks">Browse tracks →</Link>
        </Button>
      </section>
    </div>
  );
}

function Stat({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
      <div className="text-xs uppercase tracking-wider text-neutral-500">{label}</div>
      <div className={`mt-1 truncate text-lg ${mono ? "font-mono text-sm" : "font-semibold"}`}>
        {value}
      </div>
    </div>
  );
}
