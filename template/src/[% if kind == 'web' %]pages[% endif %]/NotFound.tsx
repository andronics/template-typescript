import { Link } from "react-router";

/** Any path no route matches. */
export function NotFound() {
  return (
    <>
      <h1>Not found</h1>
      <p>
        <Link to="/">Home</Link>
      </p>
    </>
  );
}
