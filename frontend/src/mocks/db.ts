// In-memory dataset built once from the factories, so list and detail
// endpoints agree with each other and mutations persist until reload.
import { faker } from "@faker-js/faker";
import {
  albumDetails,
  artistRead,
  spotifyAlbum,
  spotifyArtist,
  trackRead,
  type Schema,
} from "./factories";

function buildLibrary() {
  const artists = faker.helpers.multiple(() => artistRead(), { count: 8 });

  const albums = artists.flatMap((artist) =>
    faker.helpers.multiple(
      () =>
        albumDetails({
          artist_id: artist.id,
          artist,
        }),
      { count: { min: 1, max: 4 } },
    ),
  );

  const tracks = faker.helpers.multiple(() => trackRead(), { count: 40 });

  return { artists, albums, tracks };
}

function buildSpotifyCatalogue() {
  const artists = faker.helpers.multiple(() => spotifyArtist(), { count: 15 });
  const albums = artists.flatMap((artist) =>
    faker.helpers.multiple(() => spotifyAlbum({ artists: [artist] }), {
      count: { min: 1, max: 3 },
    }),
  );
  return { artists, albums };
}

const library = buildLibrary();
const spotify = buildSpotifyCatalogue();

export const db = {
  ...library,
  spotify,

  artistWithAlbums(artistId: string): Schema<"ArtistDetails"> | undefined {
    const artist = library.artists.find((a) => a.id === artistId);
    if (!artist) return undefined;
    return {
      ...artist,
      albums: library.albums.filter((al) => al.artist_id === artistId),
    };
  },
};
