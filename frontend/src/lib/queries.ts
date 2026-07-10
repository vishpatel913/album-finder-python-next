import { queryOptions } from "@tanstack/react-query";
import { api } from "./api";
import type { Album, Artist } from "@/types";

export const albumKeys = {
  all: ["albums"] as const,
  detail: (id: string) => ["albums", id] as const,
};

export const albumsQuery = () =>
  queryOptions({
    queryKey: albumKeys.all,
    queryFn: () => api.get<Album[]>("/album/"),
  });

export const albumQuery = (id: string) =>
  queryOptions({
    queryKey: albumKeys.detail(id),
    queryFn: () => api.get<Album>(`/album/${id}`),
  });

export const artistKeys = {
  all: ["artists"] as const,
  detail: (id: string) => ["artists", id] as const,
};

export const artistsQuery = () =>
  queryOptions({
    queryKey: artistKeys.all,
    queryFn: () => api.get<Artist[]>("/artist/"),
  });

export const artistQuery = (id: string) =>
  queryOptions({
    queryKey: artistKeys.detail(id),
    queryFn: () => api.get<Artist>(`/artist/${id}`),
  });
