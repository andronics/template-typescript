# Design records

Why template-typescript is the way it is. Copy [0000-template.md](0000-template.md) to `NNNN-short-title.md`
and add a line below. **Read this index first.** The split itself is template-base's decision 0001.

| # | Title | Status | Decision in one line |
|---|---|---|---|
| [0001](0001-typescript-overlay.md) | The typescript stack overlay | Proposed | A TypeScript project is base + this overlay (+ template-container for an image), shaped as template-python; the `web` kind; `.prettierrc.json` holds the 2-space indent; rebuilds project-template's 0009 and 0014; `integration_ci` is 0002's |
| [0002](0002-integration-ci.md) | An opt-in integration test job in CI | Accepted | `integration_ci` (bool, off) adds a `stack-ci.yml` job that runs `npm run test:integration` with contrib's build and runtime packages, and fails if vitest's JUnit report has no test or a skipped (or `todo`) one; every kind; no extras; e2e is separate |
