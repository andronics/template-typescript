# TODO

template-typescript's own outstanding work. Bugs and features with discussion belong in GitHub issues; this
file is for what maintainers (and their AI assistants) should know at a glance.

## Open

Nothing yet.

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
- A project-owned, seeded `integration.yml`, or integration tests inside the Test matrix: the job is `stack-ci.yml`'s, on the minimum Node.js ([0002](docs/decisions/0002-integration-ci.md))
- `passWithNoTests: false` in the vitest configs, or `--passWithNoTests=false` on the job's command line: the job's report check catches empty and skipped runs ([0002](docs/decisions/0002-integration-ci.md))
- An `integration_extras` analogue, or a `services:` question for the integration job: npm has no named extras, and tests start what they need themselves ([0002](docs/decisions/0002-integration-ci.md))
- Playwright (browser end-to-end tests) in the integration job: a separate record if a `web` project asks ([0002](docs/decisions/0002-integration-ci.md))
