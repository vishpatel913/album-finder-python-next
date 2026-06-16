import { useState, type FormEvent } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { Button } from './ui/button'
import { useUpdateAlbum } from '@/lib/queries'
import type { Album } from '@/types'

// Example of the "edit a field on a single entity" flow, using a Radix Dialog
// (accessible, unstyled primitive) dressed with Tailwind. Submitting fires the
// useUpdateAlbum mutation, which updates the cache on success.
export function EditAlbumDialog({ album }: { album: Album }) {
  const [open, setOpen] = useState(false)
  const [genre, setGenre] = useState(album.genre)
  const [year, setYear] = useState(String(album.year))
  const update = useUpdateAlbum(album.id)

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    update.mutate(
      { genre, year: Number(year) },
      { onSuccess: () => setOpen(false) },
    )
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <Button variant="outline">Edit</Button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[90vw] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg border border-zinc-800 bg-zinc-900 p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold text-zinc-100">
            Edit album
          </Dialog.Title>
          <Dialog.Description className="mt-1 text-sm text-zinc-400">
            {album.name}
          </Dialog.Description>

          <form onSubmit={onSubmit} className="mt-4 space-y-4">
            <label className="block">
              <span className="text-sm text-zinc-300">Genre</span>
              <input
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-zinc-100 focus:border-brand focus:outline-none"
              />
            </label>
            <label className="block">
              <span className="text-sm text-zinc-300">Year</span>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-zinc-100 focus:border-brand focus:outline-none"
              />
            </label>

            {update.isError && (
              <p className="text-sm text-red-400">
                {(update.error as Error).message}
              </p>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <Dialog.Close asChild>
                <Button type="button" variant="ghost">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button type="submit" variant="primary" disabled={update.isPending}>
                {update.isPending ? 'Saving…' : 'Save'}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
