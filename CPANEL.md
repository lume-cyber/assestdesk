# Deploy Assetdesk with cPanel

This is an alternative to Docker for a hosting account with **Setup Python App** and terminal/SSH access.

## 1. Prepare an app address

Create a dedicated subdomain under a domain you own, such as `assets.yourcompany.com`, and enable a valid SSL certificate through your hosting provider. Select the subdomain root as the app URL, with no URL path suffix. The hosting control-panel address is not necessarily the address employees will use.

Keep the application source and SQLite database **outside public_html and outside every domain’s document root**. Do not upload the source archive into a public web directory. Use cPanel File Manager to upload/extract it in your account home directory, with `manage.py` at `/home/YOUR_CPANEL_USER/assetdesk/manage.py`.

## 2. Create the Python application

In **Setup Python App → Create Application**, select:

| Setting | Value |
| --- | --- |
| Python | 3.12 if available; confirm available versions before installing |
| Application root | `assetdesk` |
| Application URL | Your dedicated subdomain, at its root |
| Startup file | `app_wsgi.py` |
| Entry point | `application` |

Use the supplied `app_wsgi.py` instead of the generated example. The filename is deliberately different from cPanel’s generated `passenger_wsgi.py` wrapper. Do not run Docker, Caddy, Gunicorn, or the Django development server on this deployment path. Passenger serves the application.

## 3. Configure the application

After installing the requirements in step 4, run the portable configurator once:

```sh
python configure.py --domain assets.yourcompany.com --timezone UTC
```

Replace the domain and timezone. This creates a private `.hosting.json`, generates a secret, initializes the database, collects static files, and runs deployment checks. Do not rerun it with `--force` during an upgrade because that replaces the secret and configuration.

Alternatively, platforms that manage environment variables can provide these values directly:

Add these through the Python app’s environment-variable settings:

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A unique random secret of at least 50 characters |
| `DEBUG` | `0` |
| `ALLOWED_HOSTS` | `assets.yourcompany.com` (replace with your domain) |
| `CSRF_TRUSTED_ORIGINS` | `https://assets.yourcompany.com` |
| `DATABASE_PATH` | `/home/YOUR_CPANEL_USER/assetdesk/assets.sqlite3` |
| `TIME_ZONE` | Your organization’s timezone, for example `Asia/Dhaka` |
| `TRUST_PROXY` | `0` |

Generate the secret in the hosting terminal with `python -c 'import secrets; print(secrets.token_urlsafe(64))'` after activating the Python environment. Store it securely and keep it unchanged. Do not use the example secret from `.env.example`. This app does not automatically read `.env` on cPanel.

Do not enable TRUST_PROXY without the host confirming that it sanitizes and overwrites the forwarded headers. The default cPanel setup relies on the WSGI HTTPS scheme supplied by the hosting web server. If you encounter HTTPS redirect loops or all users share one IP for login throttling, ask the host to confirm its WSGI/proxy configuration before changing this setting; do not disable HTTPS protections to work around it.

## 4. Install and initialize

Use the virtual-environment activation command displayed by cPanel, then change into the application directory. Install the supplied dependencies:

```sh
pip install -r requirements.txt
```

cPanel also provides **Run Pip Install** for requirements files. If installation fails because Python or the bundled SQLite library is too old, share the error with your administrator; do not substitute an unsupported old Django release.

If you chose environment variables instead of `configure.py`, the application variables may not be inherited by an SSH/terminal session. Before running management commands, set the same values there. Enter the existing secret without echoing it using Bash:

```sh
read -r -s -p 'Existing application SECRET_KEY: ' SECRET_KEY
export SECRET_KEY
export DEBUG=0
export ALLOWED_HOSTS=assets.yourcompany.com
export CSRF_TRUSTED_ORIGINS=https://assets.yourcompany.com
export DATABASE_PATH=/home/YOUR_CPANEL_USER/assetdesk/assets.sqlite3
export TRUST_PROXY=0
```

Replace the example domain and account path first. Then run:

```sh
python manage.py createsuperuser
```

Restrict source/database permissions to your hosting account and the application runtime; never use world-writable permissions. WhiteNoise serves the collected public stylesheets, so no manual copy of the source tree into public_html is required.

## 5. Restart and check

Restart from **Setup Python App**, then open the app’s HTTPS subdomain. Check login, styles, an asset creation, and access from two ordinary users assigned to different lists. Confirm each user cannot open the other list’s asset URL or export its records. Test the SQLite backup procedure in README.md using your actual DATABASE_PATH rather than the Docker commands.

The package has local automated tests, but Python installation, Passenger startup, TLS, file permissions, and database operation still need verification on your hosting account. The hosting provider will have access to server-side data; choose a plan and backup policy suitable for your organization’s records.

Reference: [Namecheap: Deploy a Django application on shared servers](https://www.namecheap.com/support/knowledgebase/article.aspx/10753/2182/how-to-deploy-a-django-application-on-shared-servers/).
