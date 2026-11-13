# Deploying the PythonAnywhere test site

The test site at https://radiantlighting321.pythonanywhere.com runs the `live` branch.

- **Automatic:** push to `live`. GitHub runs the tests, then calls the site's deploy hook,
  which runs `deploy/update.sh` (pull, migrate, collectstatic, reload). See `.github/workflows/deploy-pythonanywhere.yml`.
- **By hand:** in a PythonAnywhere Bash console run `bash ~/radiant-lighting-site/deploy/update.sh`.
- **Log:** `~/radiant-deploy.log` on PythonAnywhere.
- **Token:** `~/.radiant_deploy_token` on PythonAnywhere, copied into the GitHub secret `DEPLOY_TOKEN`.

`main` is separate and deploys to the future VPS through `.github/workflows/deploy.yml`.
