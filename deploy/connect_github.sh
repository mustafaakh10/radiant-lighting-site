#!/usr/bin/env bash
# One-off: turn the uploaded-zip folder on PythonAnywhere into a copy that updates from GitHub.
# Keeps db.sqlite3 and uploads (they are not in GitHub). Prints the deploy token for GitHub.
set -euo pipefail
source "$(dirname "$0")/pa_env.sh"
cd "$APP_DIR"
[ -d .git ] || git init --quiet
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/mustafaakh10/radiant-lighting-site.git
git fetch --quiet origin "$BRANCH"
git reset --quiet --hard "origin/$BRANCH"
git checkout --quiet -B "$BRANCH" "origin/$BRANCH"
git branch --quiet --set-upstream-to="origin/$BRANCH"
if [ ! -f "$DEPLOY_TOKEN_FILE" ]; then
  python3 -c "import secrets; print(secrets.token_urlsafe(32))" > "$DEPLOY_TOKEN_FILE"
  chmod 600 "$DEPLOY_TOKEN_FILE"
fi
bash deploy/update.sh
echo
echo "Connected to GitHub. Copy this deploy token into GitHub (Settings > Secrets > Actions, name DEPLOY_TOKEN):"
echo
cat "$DEPLOY_TOKEN_FILE"
echo
