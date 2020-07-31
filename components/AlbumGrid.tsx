import React from "react";
import styled from "styled-components";
import { useAlbumContext } from "../context/albumContext";
import AlbumTile from "./AlbumTile";

const GridContainer = styled.div`
  display: grid;
  grid-gap: 1rem;
  grid-template-columns: repeat(5, 1fr);
`;

const AlbumGrid = () => {
  const { albums } = useAlbumContext();
  return (
    <>
      <GridContainer>
        {albums.map((album, i) => (
          <AlbumTile
            key={i}
            title={album.title}
            artist={album.artist}
            image={album.image}
            releaseDate={album.releaseDate}
            url={album.url}
          />
        ))}
      </GridContainer>
    </>
  );
};

export default AlbumGrid;
