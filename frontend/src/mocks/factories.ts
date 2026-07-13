// Faker factories for every schema the mock handlers serve. Each factory is
// typed against the generated OpenAPI schemas, so `npm run gen:api` after a
// backend change surfaces drift here as a type error — that's the sync story.
// Every factory takes an `overrides` partial for per-call tweaks (ids, names).
import { faker } from "@faker-js/faker";
import type { components } from "@/types/api.gen";

export type Schema<K extends keyof components["schemas"]> =
  components["schemas"][K];

// Seeded so the catalogue is identical on every reload — stable ids mean
// bookmarkable detail pages and repeatable manual testing.
faker.seed(1);

const spotifyId = () => faker.string.alphanumeric(22);
const artwork = () => faker.image.urlPicsumPhotos({ width: 300, height: 300 });

export const artistRead = (
  overrides: Partial<Schema<"ArtistRead">> = {},
): Schema<"ArtistRead"> => ({
  id: faker.string.uuid(),
  name: faker.music.artist(),
  image_url: artwork(),
  spotify_id: spotifyId(),
  ...overrides,
});

export const albumRead = (
  overrides: Partial<Schema<"AlbumRead">> = {},
): Schema<"AlbumRead"> => ({
  id: faker.string.uuid(),
  name: faker.music.album(),
  artist_id: null,
  date_added: faker.date.past({ years: 3 }).toISOString(),
  genre: faker.music.genre(),
  year: faker.number.int({ min: 1970, max: 2025 }),
  is_compilation: faker.datatype.boolean({ probability: 0.1 }),
  artwork_url: artwork(),
  spotify_id: spotifyId(),
  ...overrides,
});

export const albumWithArtist = (
  overrides: Partial<Schema<"AlbumWithArtist">> = {},
): Schema<"AlbumWithArtist"> => ({
  ...albumRead(),
  artist: null,
  ...overrides,
});

export const trackRead = (
  overrides: Partial<Schema<"TrackRead">> = {},
): Schema<"TrackRead"> => ({
  id: faker.string.uuid(),
  name: faker.music.songName(),
  artist: faker.music.artist(),
  track_number: faker.number.int({ min: 1, max: 14 }),
  track_length: faker.number.int({ min: 90_000, max: 420_000 }),
  date_added: faker.date.past({ years: 3 }).toISOString(),
  play_count: faker.number.int({ min: 0, max: 500 }),
  spotify_id: spotifyId(),
  ...overrides,
});

// Spotify-shaped entities served by the /search/* endpoints.

export const spotifyArtist = (
  overrides: Partial<Schema<"Artist">> = {},
): Schema<"Artist"> => {
  const id = spotifyId();
  return {
    id,
    name: faker.music.artist(),
    image_url: artwork(),
    uri: `spotify:artist:${id}`,
    external_url: `https://open.spotify.com/artist/${id}`,
    ...overrides,
  };
};

export const spotifyAlbum = (
  overrides: Partial<Schema<"Album">> = {},
): Schema<"Album"> => {
  const id = spotifyId();
  return {
    id,
    name: faker.music.album(),
    image_url: artwork(),
    total_tracks: faker.number.int({ min: 4, max: 18 }),
    release_date: faker.date.past({ years: 30 }).toISOString().slice(0, 10),
    type: faker.helpers.arrayElement([
      "album",
      "single",
      "compilation",
    ] as const),
    uri: `spotify:album:${id}`,
    external_url: `https://open.spotify.com/album/${id}`,
    artists: [spotifyArtist()],
    ...overrides,
  };
};

export const spotifyTrack = (
  overrides: Partial<Schema<"Track">> = {},
): Schema<"Track"> => {
  const id = spotifyId();
  return {
    id,
    name: faker.music.songName(),
    album: null,
    artists: [spotifyArtist()],
    track_number: faker.number.int({ min: 1, max: 14 }),
    disc_number: 1,
    uri: `spotify:track:${id}`,
    explicit: faker.datatype.boolean({ probability: 0.2 }),
    external_url: `https://open.spotify.com/track/${id}`,
    ...overrides,
  };
};
