#!/bin/sh
# Template-owned: template-typescript. After `copier update` (scripts/post-update.sh runs it, and
# template-update.yml runs that): refresh package-lock.json for a changed package.json, and the
# wiki's generated sections for changed code.
set -eu
cd "$(dirname "$0")/../.."

npm install --no-audit --no-fund --loglevel=error --package-lock-only > /dev/null
node scripts/gen-wiki.ts > /dev/null
