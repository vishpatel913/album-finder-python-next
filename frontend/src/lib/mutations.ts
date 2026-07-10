import { mutationOptions } from "@tanstack/react-query";
import { api } from "./api";
import type { Album, Artist } from "@/types";

export const albumKeys = {
  all: ["albums"] as const,
  detail: (id: string) => ["albums", id] as const,
};

export const albumEnrichMutation = (id: string) =>
  mutationOptions({
    mutationKey: albumKeys.detail(id),
    mutationFn: () => api.post<Album>(`/album/${id}/enrich`, {}),
  });

export const artistKeys = {
  all: ["artists"] as const,
  detail: (id: string) => ["artists", id] as const,
};

export const artistEnrichMutation = (id: string) =>
  mutationOptions({
    mutationKey: artistKeys.detail(id),
    mutationFn: () => api.post<Artist>(`/artist/${id}/enrich`, {}),
  });
