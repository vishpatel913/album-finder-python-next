import { mutationOptions } from "@tanstack/react-query";
import { api } from "./api";
import { ALBUM_QUERY_KEYS, ARTIST_QUERY_KEYS } from "./queries";
import type { Album, Artist } from "@/types";
import { queryClient } from "./query-client";

export const ALBUM_MUTATION_KEYS = {
  all: ["albums"] as const,
  detail: (id: string) => ["albums", id] as const,
};

export const ARTIST_MUTATION_KEYS = {
  all: ["artists"] as const,
  detail: (id: string) => ["artists", id] as const,
};

export const albumEnrichMutation = (id: string) =>
  mutationOptions({
    mutationKey: ALBUM_MUTATION_KEYS.detail(id),
    mutationFn: () => api.post<Album>(`/album/${id}/enrich`, {}),
    onSuccess: (data) => {
      queryClient.setQueryData([ALBUM_QUERY_KEYS.detail, data.id], data);
      queryClient.setQueryData([ALBUM_QUERY_KEYS.all], (prev: Album[]) =>
        prev.map((p) => (p.id === data.id ? data : p)),
      );
    },
  });

export const artistEnrichMutation = (id: string) =>
  mutationOptions({
    mutationKey: ARTIST_MUTATION_KEYS.detail(id),
    mutationFn: () => api.post<Artist>(`/artist/${id}/enrich`, {}),
    onSuccess: (data) => {
      queryClient.setQueryData([ARTIST_QUERY_KEYS.detail, data.id], data);
      queryClient.setQueryData([ARTIST_QUERY_KEYS.all], (prev: Artist[]) =>
        prev.map((p) => (p.id === data.id ? data : p)),
      );
    },
  });
