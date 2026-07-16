import type { components } from "./api.gen";

// Entity types are sourced from the generated OpenAPI types (api.gen.ts) so they
// stay in lock-step with the backend. Regenerate after API changes:
//   npm run gen:api      (backend must be running on :8004)
type Schemas = components["schemas"];

export type Album = Schemas["AlbumDetails"];
export type Artist = Schemas["ArtistDetails"];

// The backend doesn't expose a TrackRead response model yet, so this stays
// hand-defined. Swap to Schemas['TrackRead'] once that endpoint lands and the
// generated file picks it up.
export interface Track {
  id: string;
  name: string;
  artist: string;
  track_number: number | null;
  track_length: number;
  date_added: string;
  play_count: number | null;
}
