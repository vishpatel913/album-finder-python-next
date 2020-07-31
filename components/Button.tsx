import styled from "styled-components";

const Button = styled.button`
  border: solid 1px #1f6dff;
  border-radius: 5px;
  background: none;
  color: #1f6dff;
  transition: all 0.2s;
  padding: 0.5rem 1rem;
  font-size: 16px;
  cursor: pointer;
  &:hover {
    color: white;
    background: #1f6dff;
  }
`;

export default Button;
