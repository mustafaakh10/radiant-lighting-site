"""Deploy hook: GitHub calls this after a push to the "live" branch, and the site updates itself.

POST /_deploy/          header X-Deploy-Token -> starts deploy/update.sh in the background (202)
GET  /_deploy/status/   header X-Deploy-Token -> last lines of the deploy log
Switched off (404) unless DJANGO_DEPLOY_TOKEN is set.
"""
import hmac
import os
import subprocess
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

LOG = Path.home() / "radiant-deploy.log"


def _check(request):
    token = getattr(settings, "DEPLOY_TOKEN", "")
    if not token:
        raise Http404
    given = request.headers.get("X-Deploy-Token", "")
    return hmac.compare_digest(given.encode(), token.encode())


@csrf_exempt
@require_POST
def deploy(request):
    if not _check(request):
        return HttpResponseForbidden("bad token")
    script = Path(settings.BASE_DIR) / "deploy" / "update.sh"
    with open(LOG, "w") as log:
        subprocess.Popen(["bash", str(script)], stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         cwd=settings.BASE_DIR, env=os.environ.copy(), start_new_session=True)
    return JsonResponse({"started": True}, status=202)


@require_GET
def status(request):
    if not _check(request):
        return HttpResponseForbidden("bad token")
    text = LOG.read_text()[-4000:] if LOG.exists() else "no deploy yet"
    return HttpResponse(text, content_type="text/plain")
