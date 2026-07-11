import React from "react";
import clsx from "clsx";
import { DownloadIcon, CheckCircledIcon } from "@radix-ui/react-icons";

import { useMutation } from "@tanstack/react-query";
import { albumEnrichMutation, artistEnrichMutation } from "@/lib/mutations";
import { Button } from "./ui/button";

interface Props {
  id: string;
  spotifyId?: string | null;
  type: "album" | "artist";
}

export const SpotifyEnrichButton: React.FC<Props> = ({
  id,
  spotifyId = null,
  type,
}) => {
  const {
    mutate: enrichAlbum,
    isPending: isAlbumPending,
    isError: isAlbumError,
  } = useMutation(albumEnrichMutation(id ?? ""));
  const {
    mutate: enrichArtist,
    isPending: isArtistPending,
    isError: isArtistError,
  } = useMutation(artistEnrichMutation(id ?? ""));

  const handleClick = () => {
    switch (type) {
      case "album":
        return enrichAlbum();
      case "artist":
        return enrichArtist();
      default:
        break;
    }
  };

  return (
    <Button
      size={"sm"}
      className={clsx({ "text-brand": spotifyId })}
      onClick={() => handleClick()}
    >
      {spotifyId ? <>♫</> : <>⎋</>}
    </Button>
  );
};
