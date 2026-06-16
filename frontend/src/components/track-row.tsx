// Ported from the Next app; props spread out and defined locally so it doesn't
// depend on a shared API type. Renders a <tr>, so use inside a <table>/<tbody>.
export interface TrackRowProps {
  name: string
  artist: string
  album: string
  genre: string
  plays: number
  year?: number | null
  rating?: number | null
  date_added?: string | null
  featured?: string | null
  featured_artists?: string[]
}

export function TrackRow({
  name,
  artist,
  album,
  genre,
  plays,
  year = null,
  rating = null,
  date_added = null,
  featured = null,
  featured_artists = [],
}: TrackRowProps) {
  return (
    <tr className="border-b border-neutral-900 hover:bg-neutral-900/50">
      <td className="px-3 py-2 font-medium">{name}</td>
      <td className="px-3 py-2 text-neutral-400">{artist}</td>
      <td className="px-3 py-2 text-neutral-500" title={featured ?? ''}>
        {featured_artists.join(', ')}
      </td>
      <td className="px-3 py-2 text-neutral-500">{album}</td>
      <td className="px-3 py-2 text-neutral-500">{genre}</td>
      <td className="px-3 py-2 text-right tabular-nums">{plays}</td>
      <td className="px-3 py-2 text-right tabular-nums text-neutral-500">{year ?? ''}</td>
      <td className="px-3 py-2 text-right text-neutral-500">{rating ? `${rating}` : ''}</td>
      <td className="px-3 py-2 text-right text-neutral-500">
        {date_added ? date_added.slice(0, 10) : ''}
      </td>
    </tr>
  )
}
