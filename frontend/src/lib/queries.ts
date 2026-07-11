import { queryOptions } from "@tanstack/react-query";
import { api } from "./api";
import type { Album, Artist } from "@/types";

export const ALBUM_QUERY_KEYS = {
  all: ["albums"] as const,
  detail: (id: string) => ["albums", id] as const,
};

export const albumsQuery = () =>
  queryOptions({
    queryKey: ALBUM_QUERY_KEYS.all,
    queryFn: () => api.get<Album[]>("/album/"),
  });

export const albumQuery = (id: string) =>
  queryOptions({
    queryKey: ALBUM_QUERY_KEYS.detail(id),
    queryFn: () => api.get<Album>(`/album/${id}`),
  });

export const ARTIST_QUERY_KEYS = {
  all: ["artists"] as const,
  detail: (id: string) => ["artists", id] as const,
};

export const artistsQuery = () =>
  queryOptions({
    queryKey: ARTIST_QUERY_KEYS.all,
    queryFn: () => api.get<Artist[]>("/artist/"),
  });

export const artistQuery = (id: string) =>
  queryOptions({
    queryKey: ARTIST_QUERY_KEYS.detail(id),
    queryFn: () => api.get<Artist>(`/artist/${id}`),
  });
