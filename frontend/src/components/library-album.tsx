import { Album } from "@/types";
import React from "react";
import { AlbumTile } from "./album-tile";
import { useMutation } from "@tanstack/react-query";
import { albumEnrichMutation } from "@/lib/mutations";
import { Button } from "./ui/button";
import clsx from "clsx";

export const LibraryAlbum = (props: Album) => {
  const { mutate } = useMutation(albumEnrichMutation(props.id));
  return (
    <AlbumTile
      name={props.name}
      artist={props.artist?.name}
      year={props.year}
      genre={props.genre}
      imageUrl={props.artwork_url}
      releaseDate={String(props.year)}
      actions={
        <Button
          size={"sm"}
          className={clsx({ "text-brand": props.spotify_id })}
          onClick={() => mutate()}
        >
          ♫
        </Button>
      }
    />
  );
};
