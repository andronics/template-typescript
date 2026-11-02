import { useRouteLoaderData } from "react-router";

import type { Config } from "../config.ts";

/** The start page: replace it with the app's own. */
export function Home() {
  const config = useRouteLoaderData<Config>("root");
  return (
    <>
      <h1>{__APP_NAME__}</h1>
      <p>Version {__APP_VERSION__}</p>
      <p>
        API: <code>{config?.apiBaseUrl}</code>
      </p>
    </>
  );
}
