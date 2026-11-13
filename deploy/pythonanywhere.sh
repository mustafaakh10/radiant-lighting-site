#!/usr/bin/env bash
# Sets up a test copy of the site on a free PythonAnywhere account.
# Run from a PythonAnywhere Bash console, inside the unzipped project folder:
#     bash deploy/pythonanywhere.sh
# Safe to re-run after uploading a newer zip: it keeps your database and uploads.
set -euo pipefail

USER_NAME="$(whoami)"
HOST="${USER_NAME}.pythonanywhere.com"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$HOME/.virtualenvs/radiant"
WSGI_FILE="/var/www/${USER_NAME}_pythonanywhere_com_wsgi.py"
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
KEY_FILE="$HOME/.radiant_secret_key"
if [ ! -f "$KEY_FILE" ]; then
  "$VENV/bin/python" -c "import secrets; print(secrets.token_urlsafe(50))" > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
fi

export DJANGO_SETTINGS_MODULE=config.settings.prod
export DJANGO_SECRET_KEY="$(cat "$KEY_FILE")"
export DJANGO_ALLOWED_HOSTS="$HOST"
export DJANGO_CSRF_TRUSTED_ORIGINS="https://${HOST}"
export WAGTAILADMIN_BASE_URL="https://${HOST}"
export DJANGO_SSL_REDIRECT=false
export DJANGO_SERVE_MEDIA=true
export DJANGO_MEDIA_ROOT="$HOME/radiant-media"
mkdir -p "$DJANGO_MEDIA_ROOT"

echo "== Database"
"$VENV/bin/python" manage.py migrate --noinput
echo "== Styles and scripts"
"$VENV/bin/python" manage.py collectstatic --noinput >/dev/null
echo "== Catalogue (existing products are kept)"
"$VENV/bin/python" manage.py seed_catalogue

echo "== Web app settings"
cat > "$WSGI_FILE" <<EOF
import os, sys
path = "${APP_DIR}"
if path not in sys.path:
    sys.path.insert(0, path)
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.prod"
os.environ["DJANGO_SECRET_KEY"] = open("${KEY_FILE}").read().strip()
os.environ["DJANGO_ALLOWED_HOSTS"] = "${HOST}"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://${HOST}"
os.environ["WAGTAILADMIN_BASE_URL"] = "https://${HOST}"
os.environ["DJANGO_SSL_REDIRECT"] = "false"
os.environ["DJANGO_SERVE_MEDIA"] = "true"
os.environ["DJANGO_MEDIA_ROOT"] = "${DJANGO_MEDIA_ROOT}"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF

if ! "$VENV/bin/python" manage.py shell -c "from django.contrib.auth import get_user_model as g; raise SystemExit(0 if g().objects.filter(is_superuser=True).exists() else 1)"; then
  echo "== Create your admin login"
  "$VENV/bin/python" manage.py createsuperuser
fi

touch "$WSGI_FILE"
echo
echo "Done. In the Web tab set Virtualenv to: $VENV"
echo "Then press Reload and open https://${HOST}  (admin: https://${HOST}/admin/)"
