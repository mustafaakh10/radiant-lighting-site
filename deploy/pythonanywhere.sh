#!/usr/bin/env bash
# Sets up a test copy of the site on a free PythonAnywhere account.
# Run from a PythonAnywhere Bash console, inside the unzipped project folder:
#     bash deploy/pythonanywhere.sh
# Safe to re-run after uploading a newer zip: it keeps your database and uploads.
set -euo pipefail

source "$(dirname "$0")/pa_env.sh"
PY="python3.12"

echo "== Radiant Lighting test site for https://${HOST}"
cd "$APP_DIR"

if [ ! -d "$VENV" ]; then
  echo "== Creating Python environment (one-off, takes a few minutes)"
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r requirements.txt

# A secret key that stays the same between re-runs.
if [ ! -f "$KEY_FILE" ]; then
  "$VENV/bin/python" -c "import secrets; print(secrets.token_urlsafe(50))" > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
fi

export DJANGO_SECRET_KEY="$(cat "$KEY_FILE")"
mkdir -p "$DJANGO_MEDIA_ROOT"

echo "== Database"
"$VENV/bin/python" manage.py migrate --noinput
echo "== Styles and scripts"
"$VENV/bin/python" manage.py collectstatic --noinput >/dev/null
echo "== Catalogue (existing products are kept)"
"$VENV/bin/python" manage.py seed_catalogue
"$VENV/bin/python" manage.py seed_projects
"$VENV/bin/python" manage.py seed_rooms

echo "== Web app settings"
write_wsgi

if ! "$VENV/bin/python" manage.py shell -c "from django.contrib.auth import get_user_model as g; raise SystemExit(0 if g().objects.filter(is_superuser=True).exists() else 1)"; then
  echo "== Create your admin login"
  "$VENV/bin/python" manage.py createsuperuser
fi

touch "$WSGI_FILE"
echo
echo "Done. In the Web tab set Virtualenv to: $VENV"
echo "Then press Reload and open https://${HOST}  (admin: https://${HOST}/admin/)"
