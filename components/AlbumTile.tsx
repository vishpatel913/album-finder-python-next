import qs from "querystring";
import React from "react";
import styled from "styled-components";
import moment from "moment";
import {
  FaGoogle,
  FaSpotify,
  // FaMinusCircle,
  // FaPlusCircle,
  // FaMinusCircle,
} from "react-icons/fa";
import { Album } from "../interfaces/album";
// import { useAlbumContext } from "../context/albumContext";

// interface Props extends Album {
//   onFilter?: (artist: string) => void;
// }

const TileContainer = styled.div`
  position: relative;
`;
const AlbumArt = styled.img`
  width: 100%;
  transition: all 0.2s;
  &:hover {
    opacity: 0.7;
  }
`;
const DetailsContainer = styled.div`
  text-align: left;
`;
const Title = styled.strong`
  font-size: 16px;
  font-weight: 400;
  margin: 0.5rem 0 0;
`;
const Text = styled.p`
  margin: 0.5rem 0;
  font-size: 12px;
`;
const FlexContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: bottom;
  div {
    display: flex;
  }
`;
const Link = styled.a`
  display: block;
  margin: 0.5rem 0;
  font-size: 16px;
  color: #1f6dff;
  text-decoration: none;
  padding: 0.25rem;
  transition: all 0.2s;
`;

const AlbumTile = ({ title, artist, image, releaseDate, url }: Album) => {
  const formattedDate = moment(releaseDate).format("Do MMMM YYYY");
  // const { setArtistFilters } = useAlbumContext();

  return (
    <TileContainer>
      <AlbumArt src={image} alt={title} />
      <DetailsContainer>
        <FlexContainer>
          <Title>{title}</Title>
          <div>
            <Link href={url} target="_blank" rel="noopener noreferrer">
              <FaSpotify />
            </Link>
            <Link
              href={`https://www.google.com/search?${qs.encode({
                q: title + " " + artist,
              })}`}
              target="_blank"
              rel="noopener noreferrer">
              <FaGoogle />
            </Link>
            {/* <Link onClick={() => onFilter(artist)}>
              <FaMinusCircle />
            </Link> */}
          </div>
        </FlexContainer>
        <Text>{artist}</Text>
        <Text>{formattedDate}</Text>
      </DetailsContainer>
    </TileContainer>
  );
};

export default AlbumTile;
