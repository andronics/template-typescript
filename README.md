# template-typescript

The stack overlay for a **TypeScript** project (Node.js, npm, ESLint, Prettier, tsc, vitest with an 80% floor, commander, Fastify; Vite + React for `web`).
It goes on top of [template-base](https://github.com/andronics/template-base):

```sh
uvx copier copy --trust gh:andronics/template-base my-project
uvx copier copy --trust gh:andronics/template-typescript my-project
uvx copier copy --trust gh:andronics/template-container my-project   # with container_image: the image's workflows, docker/k8s manifests
```

It asks `kind` (`service`, `cli`, `library`, `web`) and the TypeScript questions, and reads the project's identity from
base's answers. It needs template-base `v1.0.0` or later.

## What it adds

| Path | What |
|---|---|
| `package.json`, `src/`, `tests/` | The package skeleton: config (`<PREFIX>_<KEY>_FILE` > env > file > default), CLI, HTTP API; unit and opt-in integration tests; for `web`, an SPA served by nginx. `src/` and `tests/` are the project's once written |
| Slots | `.agents/stack.md`, `stack-ci.yml` (tests, integration, Markdown lint, manifests), `.gitignore`, `.pre-commit-config.yaml`, `.claude/settings.json`, `README.md`, `.github/dependabot.yml` |
| `typescript-release.yml`, `release-please-config.json`, `CHANGELOG.md` | Releases from Conventional Commits |
| `typescript-wiki.yml`, `docs/wiki/`, `scripts/gen-wiki.ts`, `scripts/check-wiki.py` | The wiki, checked and mirrored to the GitHub wiki |
| `scripts/checks.d/20-typescript.sh` | Wiki standard, version and lock file, inside base's `ci` |
| `Dockerfile`, `contrib/systemd/` | With `container_image`; with `contrib: [systemd]` |
| `docs/design/`, `docs/ai/`, `CONTRIBUTING.md`, `SECURITY.md`, `TODO.md` | Design records, prompts, the usual files |

## Setup notes

- **Required check:** branch protection names `ci` (base-ci.yml), whatever the stack.
- **Release PRs and CI:** PRs opened with the default `GITHUB_TOKEN` don't trigger CI. The organisation's
  release GitHub App (`RELEASE_APP_CLIENT_ID` variable, `RELEASE_APP_PRIVATE_KEY` secret) fixes that.
- **The wiki:** the GitHub wiki exists once its first page is created in the web UI; `typescript-wiki.yml`
  publishes `docs/wiki/` there from then on.

## Where this came from

Built from [metalayerlab/project-template](https://github.com/metalayerlab/project-template) `v0.1.23`'s
`layers/typescript/` and its TypeScript-gated core files, as a new repository with no history.
[`docs/decisions/0001`](docs/decisions/0001-typescript-overlay.md) rebuilds the records that still apply.

## License

[Unlicense](LICENSE).
