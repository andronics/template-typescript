# TODO

template-typescript's own outstanding work. Bugs and features with discussion belong in GitHub issues; this
file is for what maintainers (and their AI assistants) should know at a glance.

## Open

- No CI job runs the integration tests: projects get `npm run test:integration` and `tests/integration/`, but nothing runs them (template-python has `integration_ci`). Proposed in [0002](docs/decisions/0002-integration-ci.md).

## Decided against (don't re-propose without reading this first)

<!-- One line each: the idea, why not, and a link to the issue, PR or design record. Carried from
project-template v0.1.23's TODO.md; its records are in its docs/design/. -->

- A separate front-end language layer (`typescript-frontend`): same toolchain, different shape, so it is a `kind` (project-template [0009](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0009-typescript-layer.md))
- Express, Hono, Biome, tsx, pnpm/yarn, a bundler, Jest or semantic-release in the TypeScript stack (project-template [0009](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0009-typescript-layer.md))
- Firebase deploy, Storybook, Chrome extensions, Electron or npm workspaces in the skeleton: one project's choice, not a skeleton's (project-template [0009](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0009-typescript-layer.md))
- Node (Fastify) serving a `web` app's files, or Caddy/Alpine/unprivileged nginx images: the official Debian nginx with a uid 1000 user (project-template [0014](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0014-web-kind.md))
- Build-time `VITE_*` config or an entrypoint-written `window.__ENV__` for a `web` app: a mounted `/config.json` read at run time (project-template [0014](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0014-web-kind.md))
- TanStack Router, wouter, hash URLs or React Router's declarative/framework modes: React Router in data mode (project-template [0014](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0014-web-kind.md))
- TanStack Query, zustand, Tailwind, Storybook, msw or Playwright in the `web` skeleton: one project's choice (project-template [0014](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0014-web-kind.md))
- systemd for `kind: web`: a host's own nginx serves static files (project-template [0014](https://github.com/metalayerlab/project-template/blob/v0.1.23/docs/design/0014-web-kind.md))
