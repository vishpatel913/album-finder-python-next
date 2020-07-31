import React from "react";
import styled from "styled-components";
import { GetStaticProps } from "next";
import moment from "moment";
import { Album } from "../interfaces/album";
import AlbumGrid from "../components/AlbumGrid";

import albumsData from "../data/albums.json";
import { AlbumProvider } from "../context/albumContext";

interface Props {
  albums: Album[];
  updated?: string;
}

interface Cache {
  updated?: string;
}

const Layout = styled.div`
  @import url("https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;600&display=swap");
  font-family: "Quicksand", sans-serif;
  font-weight: 300;
  margin-bottom: 2rem;
`;
const Toolbar = styled.nav`
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  background: #1f6dff;
  position: absolute;
  height: 4rem;
  top: 0;
  left: 0;
  right: 0;
  img {
    margin-right: 1rem;
  }
  h1 {
    font-weight: 400;
    em {
      font-size: 16px;
      font-weight: 200;
    }
  }
`;
const Content = styled.div`
  margin-top: 4rem;
  padding: 1rem;
`;

const cache: Cache = { updated: undefined };

const HomePage = ({ albums, updated }: Props) => {
  return (
    <Layout>
      <Toolbar>
        <img
          src="https://vishpatel.com/images/logo-light.png"
          alt="logo"
          width="32px"
        />
        <h1>
          Latest Album Releases <em>(updated {updated})</em>
        </h1>
      </Toolbar>
      <AlbumProvider allAlbums={albums}>
        <Content>
          <AlbumGrid />
        </Content>
      </AlbumProvider>
    </Layout>
  );
};

export const getStaticProps: GetStaticProps = async (): Promise<{
  props: Props;
}> => {
  const updated = cache.updated || moment().format("Do MMM YYYY");
  cache.updated = updated;

  return {
    props: {
      albums: albumsData,
      updated,
    },
  };
};

export default HomePage;
