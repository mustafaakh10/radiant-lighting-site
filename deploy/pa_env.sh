# Shared settings for the PythonAnywhere scripts. Sourced, not run.
USER_NAME="$(whoami)"
HOST="${USER_NAME}.pythonanywhere.com"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$HOME/.virtualenvs/radiant"
WSGI_FILE="/var/www/${USER_NAME}_pythonanywhere_com_wsgi.py"
KEY_FILE="$HOME/.radiant_secret_key"
DEPLOY_TOKEN_FILE="$HOME/.radiant_deploy_token"
BRANCH="live"

export DJANGO_SETTINGS_MODULE=config.settings.prod
[ -f "$KEY_FILE" ] && export DJANGO_SECRET_KEY="$(cat "$KEY_FILE")"
export DJANGO_ALLOWED_HOSTS="$HOST"
export DJANGO_CSRF_TRUSTED_ORIGINS="https://${HOST}"
export WAGTAILADMIN_BASE_URL="https://${HOST}"
export DJANGO_SSL_REDIRECT=false
export DJANGO_SERVE_MEDIA=true
export DJANGO_MEDIA_ROOT="$HOME/radiant-media"

# Free accounts reach the internet through PythonAnywhere's proxy. Consoles set this already; web workers may not.
if [ -z "${https_proxy:-}" ] && getent hosts proxy.server >/dev/null 2>&1; then
  export http_proxy=http://proxy.server:3128 https_proxy=http://proxy.server:3128
fi

write_wsgi() {
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
os.environ["DJANGO_SITE_NOINDEX"] = "true"
if os.path.exists("${DEPLOY_TOKEN_FILE}"):
    os.environ["DJANGO_DEPLOY_TOKEN"] = open("${DEPLOY_TOKEN_FILE}").read().strip()
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF
}
