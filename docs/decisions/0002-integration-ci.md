# 0002: An opt-in integration test job in CI

Status: Proposed
Date: 2026-11-02
Authors: Stephen Cox; drafted by Claude (Claude Code)

## Context

Every TypeScript project gets `tests/integration/` and `npm run test:integration`
(`RUN_INTEGRATION=1 vitest run`, which selects `tests/integration/**`), but no CI job runs them. 0001 left
out template-python's `integration_ci`; project-template's 0017 deferred it because vitest passes with no
tests in that mode (`passWithNoTests: integration` in `vitest.config.ts` and `vite.config.ts`), so a
TypeScript job needs its own way to fail when nothing runs.

As 0017: the job must fail, never pass vacuously, when no test runs or one is skipped (a missing package,
device or service). A project that leaves it off sees no diff on update. The answers file is a public
interface.

## Decision

- **Copier question `integration_ci`**: `type: bool`, default `false`, asked for every kind. Help text as
  template-python's. No extras question.
- **A job `integration`, named Integration tests**, in `stack-ci.yml` when it is on, on `node_version` only
  (the Test job covers every version):
  1. checkout and `actions/setup-node` (same pins, `cache: npm`);
  2. installs both lists in `contrib/system-packages.txt`, `build:` and `runtime:`, with template-python's
     `sed` (none listed: nothing installed);
  3. `npm ci --no-audit --no-fund`;
  4. `npm run test:integration -- --reporter=default --reporter=junit
     --outputFile.junit="$RUNNER_TEMP/integration.xml"`; no coverage, which is the unit tests' floor;
  5. a `python3` step (as `checks.d/20-typescript.sh` uses) that reads the report and fails, naming each
     test, if the report is missing, holds no test case, or any case is `<skipped>` (vitest's `skip`,
     `skipIf` and `todo`). An expected failure is `test.fails`, which reports as passed.
     Checked with vitest 5.0.5: with no tests it exits 0 and writes a report with `tests="0"`; `skip`,
     `skipIf` and `todo` each write `<skipped/>`; `test.fails` writes a plain passed case.
- **`passWithNoTests` stays** in both configs: a local `npm run test:integration` with no tests still passes.
  The report check is the job's "fail when empty", and it catches skips too.
- **It runs under base-ci's `ci`**, the one required check, so it is required once on; there is no separate
  check to add to branch protection.
- **Wiki for new projects**: `includes/wiki/testing-run.md.jinja` says the job runs, when it is on.
- **Tests**: the question set test gains `integration_ci`; `service-image`, `library` and `web` turn it on,
  so actionlint and every Definition of done see the job; a test runs the rendered steps 4 and 5 against no
  tests, a passing test plus a `test.fails`, a `skip` and a `todo`.

### Web

`web` gets it too. It has the script and the folder, and its integration tests (jsdom, against a real API
or `/config.json` served by something) are as real as a service's. A kind switch would add a validator and
a branch to save nothing: the default is off.

Browser end-to-end tests (Playwright) are a separate concern and not this job: they need browsers
installed, a built app served, and their own runner, not vitest. Playwright in the `web` skeleton is
already in TODO.md's "Decided against". A project that needs it in CI asks, and gets its own record.

## Alternatives considered

- **A project-owned `integration.yml`, seeded by the template**: it would never receive fixes (pins, the
  report check). As 0017.
- **Integration tests inside the Test matrix**: they would run on every Node version, slow each entry and
  not say which kind of test failed. As 0017.
- **`passWithNoTests: false` in the configs**: both are template-owned, so it would reach every project and
  fail a local `npm run test:integration` in any project with no integration tests yet, job or not; and it
  doesn't catch skips, so the report check is needed anyway.
- **`--passWithNoTests=false` on the job's command line**: catches empty, not skipped; the report check does
  both in one place.
- **An `integration_extras` analogue**: npm installs `optionalDependencies` by default, and there is
  nothing like pyproject's named extras to choose. Not needed.
- **Excluding `web`**: see Web above.
- **A `services:` question (a database container for the job)**: hosted runners have Docker, so the tests
  can start what they need themselves (testcontainers). Not until a project needs more.
- **The job in template-base**: base never names a stack; the command is this stack's.

## Consequences

- **Copier**: one new question, `integration_ci`. Permanent once given; changing its shape needs a
  migration. Template-python's `integration_extras` has no counterpart.
- **Projects with it on** get the Integration tests job, required through `ci`. A test that skips on a
  missing precondition fails it: such tests use `test.fails`, or live outside `tests/integration/`. They
  list the packages they need in `contrib/system-packages.txt`.
- **Projects with it off**: no diff.
- **Migration**: no TypeScript project exists yet (0001). One that does:
  `uvx copier update --trust -a .copier-answers.stack-typescript.yml -d integration_ci=true`. Testing-Guide
  is project-owned, so it doesn't change: add the paragraph by hand.
- **Budget**: none. `.agents/stack.md` already lists `npm run test:integration` and `RUN_INTEGRATION=1`,
  and "never skip a test" is in its Conventions.
- **Release**: `feat:`, a minor release. 0001's "no `integration_ci`" line and its index entry change when
  this is implemented; the rejected alternatives go into TODO.md's "Decided against".

## Open questions

1. **Every kind, or not `web`?** Recommend every kind: same script, same folder, default off, no branch.
2. **Fail on `todo` as well as `skip`?** Recommend yes: a `todo` in an on-by-answer job is a test that
   doesn't run, which is what the job exists to catch. A project keeps unfinished tests out of
   `tests/integration/`.
3. **Leave `passWithNoTests: integration` in the configs?** Recommend yes: the job enforces non-empty,
   and a project with no integration tests yet keeps a green local run.
4. **Playwright/e2e**: confirm it is out of scope, a separate record if a `web` project asks. Recommend
   yes: different tools, different runner, and the skeleton already declines Playwright.
