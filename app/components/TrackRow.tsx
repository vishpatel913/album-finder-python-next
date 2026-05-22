import type { TrackRow as TrackRowT } from "@/app/lib/api";

export function TrackRow({ track }: { track: TrackRowT }) {
  return (
    <tr className="border-b border-neutral-900 hover:bg-neutral-900/50">
      <td className="px-3 py-2 font-medium">{track.name}</td>
      <td className="px-3 py-2 text-neutral-400">{track.artist}</td>
      <td className="px-3 py-2 text-neutral-500">{track.album}</td>
      <td className="px-3 py-2 text-neutral-500">{track.genre}</td>
      <td className="px-3 py-2 text-right tabular-nums">{track.plays}</td>
      <td className="px-3 py-2 text-right tabular-nums text-neutral-500">{track.year ?? ""}</td>
      <td className="px-3 py-2 text-right text-neutral-500">
        {track.rating ? `${track.rating}` : ""}
      </td>
      <td className="px-3 py-2 text-right text-neutral-500">
        {track.date_added ? track.date_added.slice(0, 10) : ""}
      </td>
    </tr>
  );
}
