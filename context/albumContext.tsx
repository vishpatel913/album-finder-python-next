import React, { createContext, useContext, ReactNode } from "react";
import { Album } from "../interfaces/album";

interface Props {
  allAlbums: Album[];
  children: ReactNode;
}

interface State {
  albums: Album[];
}

const intialState: State = {
  albums: [],
};

export const AlbumContext = createContext<State>(intialState);

export const useAlbumContext = () => useContext(AlbumContext);

export const AlbumProvider = ({ allAlbums, children }: Props) => {
  const albums = allAlbums
    .filter(i => (i.acc || 0) < 15)
    .sort((a: Album, b: Album) => (a.releaseDate < b.releaseDate ? 1 : -1));

  const ctx = {
    albums,
  };

  return <AlbumContext.Provider value={ctx}>{children}</AlbumContext.Provider>;
};
