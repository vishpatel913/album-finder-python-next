import React from "react";
import styled from "styled-components";

const Layout = styled.div`
  @import url("https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;600&display=swap");
  font-family: "Quicksand", sans-serif;
  font-weight: 300;
  margin: 2rem;
`;

const HomePage = () => {
  return (
    <Layout>
      <div>
        <h2>Test Upload</h2>
      </div>
    </Layout>
  );
};

export default HomePage;
