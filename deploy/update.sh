#!/usr/bin/env bash
# Update the PythonAnywhere site from GitHub (branch "live"), then reload it.
#     bash ~/radiant-lighting-site/deploy/update.sh
# Also run automatically by the deploy hook when GitHub pushes. Keeps the database and uploads.
set -uo pipefail
source "$(dirname "$0")/pa_env.sh"
# Only on PythonAnywhere: this resets the folder to GitHub, which would wipe local work elsewhere.
[ -d /var/www ] && [ -n "${PYTHONANYWHERE_DOMAIN:-}${PYTHONANYWHERE_SITE:-}" -o -f "$WSGI_FILE" ] || { echo "Not on PythonAnywhere, stopping."; exit 1; }
LOG="$HOME/radiant-deploy.log"
exec 9>"$HOME/.radiant_deploy.lock"
flock -n 9 || { echo "Another update is already running."; exit 0; }

fail() { echo "DEPLOY FAILED: $1 ($(date '+%F %T'))"; exit 1; }
echo "== Update started $(date '+%F %T')"
cd "$APP_DIR" || fail "no project folder"

echo "== Getting the latest code from GitHub ($BRANCH)"
git fetch --quiet origin "$BRANCH" || fail "could not reach GitHub"
git reset --quiet --hard "origin/$BRANCH" || fail "could not update files"
echo "   now at $(git log -1 --format='%h %s')"

# Re-read this script's settings in case the update changed them.
source "$APP_DIR/deploy/pa_env.sh"

REQ_HASH="$(sha256sum requirements.txt | cut -c1-16)"
if [ "$(cat "$HOME/.radiant_req_hash" 2>/dev/null)" != "$REQ_HASH" ]; then
  echo "== Installing packages (requirements changed)"
  "$VENV/bin/pip" install --quiet -r requirements.txt || fail "package install"
  echo "$REQ_HASH" > "$HOME/.radiant_req_hash"
fi

mkdir -p "$DJANGO_MEDIA_ROOT"
echo "== Database"
"$VENV/bin/python" manage.py migrate --noinput || fail "database migration"
echo "== Styles and scripts"
"$VENV/bin/python" manage.py collectstatic --noinput >/dev/null || fail "collectstatic"
"$VENV/bin/python" manage.py seed_catalogue >/dev/null || true
"$VENV/bin/python" manage.py seed_projects || true
"$VENV/bin/python" manage.py seed_guides || true
"$VENV/bin/python" manage.py seed_rooms || true

write_wsgi
touch "$WSGI_FILE"   # reloads the web app
echo "DEPLOY OK $(git log -1 --format='%h') $(date '+%F %T')"
