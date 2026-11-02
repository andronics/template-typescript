# 0001: The typescript stack overlay

Status: Proposed
Date: 2026-11-02
Authors: Stephen Cox

## Context

project-template made a TypeScript project with `language: typescript`, through `layers/typescript/` and the
core files gated on it (its design records 0009 and 0014). template-base's decision **0001** (from the idea
note **🥞 Stacked Copier Templates**, in the brain's `vault/ideas/`) splits that template into a base and one
stack overlay per project; where the two disagree, template-base's 0001 wins. This repository is the overlay
for TypeScript, built from project-template `v0.1.23`'s files as a new repository with no history. It has
the same shape as template-python, whose decision 0001 records the choices both share. This record states
what differs.

No project uses TypeScript yet, so the render matrix alone proves it: every kind, with and without an image
and contrib, through its own Definition of done.

## Decision

- **A TypeScript project is base + this overlay** (+ template-container for an image's workflows and the
  docker and k8s manifests). It writes `.copier-answers.stack-typescript.yml` and fails unless base is
  `v2.0.0` or later. It reads base's answers as template-python does, through the recorded `base_answers`
  (template-base 0001's pattern), because `copier update` replays without base's answers file. It fills
  base 2.0.0's PR-template and issue-config slots as template-python does.
- **Asks** `kind` (`service`, `cli`, `library`, **`web`**), `node_version`, `port`, `extra_ports`,
  `health_path`, `container_image`, `contrib`, `puid_pgid`, `timezone`. These are project-template's
  TypeScript questions, unchanged. `has_cli` is derived (`kind in [service, cli]`). It has no
  `image_extras`, which was Python's. `integration_ci` came later, in [0002](0002-integration-ci.md).
- **The web kind** (was 0014): Vite + React 19 and React Router 8 (data mode), run-time `/config.json`,
  served by nginx as uid 1000. `index.html`, `public/config.json` and `docker/nginx-site.conf` are the
  project's once written; `docker/nginx.conf` is this overlay's. With an image, template-container's
  smoke test checks that `/` and a deep route both return the app's shell.
- **Slots** as template-python's, with npm, ESLint, Prettier, tsc and vitest. `stack-ci.yml` holds the test
  matrix (lint, format, typecheck, vitest with its 80% floor, a build for web or an import and CLI smoke
  test otherwise, and `gen-wiki.ts --check`), plus Markdown lint and the manifest check.
- **`scripts/checks.d/20-typescript.sh`:** the wiki standard, and semver agreement between `package.json`,
  `package-lock.json` and `.release-please-manifest.json`. It reads JSON with `python3`, so base-ci's
  `checks` job, which installs only uv, needs no Node.js.
- **Drop-ins:** `bootstrap.d/20-typescript.sh` (`npm install` and gen-wiki) and
  `post-update.d/20-typescript-npm-lock.sh` (`npm install --package-lock-only` and gen-wiki).
- **`typescript-release.yml`:** release-type `node`, which bumps the lock file itself, so it needs no
  lock job. Like Python's, it doesn't call the image build.
- **Indentation:** `.prettierrc.json` sets `tabWidth: 2`. project-template put the 2-space section in
  `.editorconfig`, which base now owns without it, and Prettier reads `.editorconfig`.

## Alternatives considered

As template-python's 0001. Also:

- **Ask base to put the TypeScript section back in `.editorconfig`:** base would name a language. *Rejected*
  for `.prettierrc.json`. Editors that read only `.editorconfig` indent `.ts` with base's default of 4
  until Prettier formats the file.

## Consequences

- With the layer gone, the files that came from project-template's `kind: web` gates render exactly as
  before: a converter checked that project-template v0.1.23 and this overlay render identically for every
  TypeScript kind.
- `scripts/post-update.d/20-typescript-npm-lock.sh` runs with whatever Node.js the runner image has in
  `template-update.yml`, which installs only uv (template-base#4).

## Open questions

None.
