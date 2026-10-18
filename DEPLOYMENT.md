# Assetdesk deployment guide

Assetdesk runs on Python 3.12 or newer. It can be deployed on any host that supports either Docker Compose or a persistent Python WSGI application. A static-only website host cannot run it because accounts, permissions, uploads, and records require server-side Python and a persistent database.

## Docker Compose

Use this for a VPS, cloud VM, dedicated server, or NAS with Docker and ports 80/443 available.

1. Point your domain's DNS to the server.
2. Copy `.env.example` to `.env`, then set the domain, time zone, and a random secret.
3. Run `docker compose up -d --build`.
4. Run `docker compose exec app python manage.py createsuperuser`.
5. Open the configured HTTPS domain.

Caddy obtains and renews the TLS certificate. Application data, including private asset pictures, is stored in the persistent `asset_data` volume.

## cPanel / Passenger

Use [CPANEL.md](CPANEL.md). Set the startup file to `app_wsgi.py`, install `requirements.txt`, and run:

```sh
python configure.py --domain assets.example.com --timezone UTC
python manage.py createsuperuser
```

Use the Python executable from cPanel's virtual environment. Add `--proxy` only when the hosting provider controls and overwrites the `X-Forwarded-Proto` header.

## Ordinary WSGI hosting

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python configure.py --domain assets.example.com --timezone UTC --proxy
python manage.py createsuperuser
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

Configure the hosting platform or an HTTPS reverse proxy to send traffic to Gunicorn. Run it under the platform's service manager, keep `.hosting.json` and `assets.sqlite3` private, and back up the database regularly.

## Updates

Back up the database, replace application files while preserving `.hosting.json` and `assets.sqlite3`, reinstall `requirements.txt`, then run:

```sh
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Restart the web process after the checks pass.
