import { queryOptions, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from './api'
import type { Album } from '@/types'

// Centralised query keys keep cache invalidation honest: mutate -> invalidate
// the exact keys that just went stale.
export const albumKeys = {
  all: ['albums'] as const,
  detail: (id: string) => ['albums', id] as const,
}

export const albumsQuery = () =>
  queryOptions({
    queryKey: albumKeys.all,
    queryFn: () => api.get<Album[]>('/album/'),
  })

export const albumQuery = (id: string) =>
  queryOptions({
    queryKey: albumKeys.detail(id),
    queryFn: () => api.get<Album>(`/album/${id}`),
  })

// The write side of your flow: click -> mutate -> cache updates.
// NOTE: the backend PUT /album/{id} endpoint is still on the to-do list. This
// hook is wired and ready; the call will 405 until that route exists. Once it
// does, nothing here needs to change.
export function useUpdateAlbum(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (patch: Partial<Omit<Album, 'id'>>) =>
      api.put<Album>(`/album/${id}`, patch),
    onSuccess: (updated) => {
      // Write the fresh entity straight into the detail cache...
      qc.setQueryData(albumKeys.detail(id), updated)
      // ...and mark the list stale so it refetches when next viewed.
      qc.invalidateQueries({ queryKey: albumKeys.all })
    },
  })
}
