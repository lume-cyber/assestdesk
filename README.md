# Assetdesk

A web application for tracking any organizational product or asset, with separate username/password accounts, role-based controls, and server-enforced access to asset lists.

For application workflows and role instructions, see [USER_GUIDE.md](USER_GUIDE.md).

## Included

- Searchable asset register, filters, pagination, and CSV exports.
- Tags, serial numbers, flexible product category, assignee, location, purchase date/value/currency, warranty, notes, and lifecycle status.
- Asset lists with independent Viewer or Editor access per user.
- Super admins and general admins manage accounts, lists, and memberships from the main website.
- General users retain per-list Viewer/Editor access; Auditors can read/export all lists; Accounts can read/export all lists and update purchase values.
- Editors register and update assets only within their authorized lists. Viewers have read/export access only. Users without memberships see no assets. Administrators see all assets.
- Audit history for asset creation and edits; Django administration logs account and permission changes.
- XLSX/CSV import into permitted lists, private asset pictures, service history, and assignment/return history.
- Password hashing, CSRF protection, secure session cookies, HTTPS, password changes, and database-backed login throttling (five failures, fifteen-minute cooldown).

## Deployment choices

See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker Compose, cPanel/Passenger, and ordinary WSGI hosting. The package supports Python 3.9+ hosts with persistent storage. Static-only website hosting cannot run this application.

## cPanel shared hosting

For a hosting account with **Setup Python App**, use [CPANEL.md](CPANEL.md). A Passenger entry point is included; Docker is not needed for this route. Availability on your specific hosting plan must be confirmed.

## Deploy on a server with Docker Compose

Requirements: a Linux server running Docker with the Compose plugin, a domain pointed to the server, and inbound ports 80/443. This package runs Django with a persistent SQLite database and Caddy-managed HTTPS. No paid application service is required.

1. Copy this folder onto the server.
2. Copy `.env.example` to `.env` and edit `DOMAIN`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` for your domain. Do not include `https://` in DOMAIN or ALLOWED_HOSTS. Set the organization’s TIME_ZONE if needed.
3. Generate a secret with `python3 -c 'import secrets; print(secrets.token_urlsafe(64))'` and place the value in SECRET_KEY. Protect `.env` and do not commit it.
4. Run `docker compose up -d --build`.
5. Create the first administrator: `docker compose exec app python manage.py createsuperuser`. Follow the prompts. No accounts or default passwords ship with the application.
6. Open `https://YOUR-DOMAIN` and sign in.

Caddy terminates HTTPS and overwrites forwarded client/protocol headers. The app has no public host port. If changing the proxy, preserve this trust boundary. Add the real hostname to ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS; do not use wildcards. This is a single-server deployment: do not scale SQLite across independent instances.

## Internal company server

For a private network hostname (for example, assets.corp.internal), point internal DNS to the server and use that hostname in `.env`. Launch with:

```sh
docker compose -f compose.yaml -f compose.internal.yaml up -d --build
```

This uses Caddy’s private certificate authority. Your IT administrator must distribute its root certificate to employee devices through the organization’s trusted-certificate policy before users browse the app. Export it with `docker compose cp proxy:/data/caddy/pki/authorities/local/root.crt ./assetdesk-root.crt`. Do not distribute the private key. Alternatively, have IT configure the company’s existing reverse proxy and approved TLS certificate. Keep HTTPS enabled in either case. Restrict server firewall access to the company network or VPN if the application is internal-only. Do not expose the Django container directly.

The Docker image uses Linux containers. A Windows Server deployment requires a supported Linux container host or Linux VM; do not assume Docker Desktop is available on a server. Final deployment depends on the server OS, available container runtime, DNS, and certificate policy.

## First-time administration

1. Select **Lists** and use the form to add a list (for example, Office assets or Finance records).
2. Select **People**, create each employee account, and choose General admin, General user, Auditor, or Accounts. Only a super admin can create another super admin.
3. For general users, open each list and add Viewer or Editor access. One person can have different permissions on different lists.
4. Return to **Asset register** and choose **Add asset**. The selected list determines who can see it. Assigning an employee name does not grant that employee access.
5. Employees sign in with their own account and change their password from the sidebar.

There is no public registration or email password reset. Administrators reset forgotten passwords using the user administration page. Use a trusted channel to deliver initial/reset credentials. Deactivate accounts to remove sign-in access; remove memberships to revoke individual lists. Unlock a rate-limited account early with `docker compose exec app python manage.py axes_reset_username USERNAME`.

To remove equipment from active use, change its status to **Retired**. There is deliberately no destructive asset deletion in the app. Editors may move an asset only between lists where they have Editor access. Its existing history follows it to the destination list. Assignment history is separate from account access and never grants permissions.

## Local development

Use Python 3.9+:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export DEBUG=1
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. DEBUG=1 is for local use only. Production requires HTTPS and DEBUG=0. Environment variables are read from the process; Docker Compose reads `.env` automatically, but local Python does not.

## Validation

```sh
python manage.py test inventory
python manage.py check --deploy
```

Run deployment checks with DEBUG=0 and a generated SECRET_KEY. Tests cover anonymous access, viewer/editor isolation, hidden asset URLs, hidden-list search and export, invalid list changes, immediate revocation, CSRF, login lockout, inactive accounts, password changes, and audit creation. The Docker image and live HTTPS deployment must also be verified on the destination server.

## Backups and maintenance

The `asset_data` Docker volume contains the application database, accounts, permissions, audit events, and sessions. Back it up regularly and before upgrades. Use SQLite’s backup API for a consistent copy while running:

```sh
docker compose exec app python -c "import sqlite3; s=sqlite3.connect('/data/assets.sqlite3'); d=sqlite3.connect('/data/backup.sqlite3'); s.backup(d); d.close(); s.close()"
docker compose cp app:/data/backup.sqlite3 ./assetdesk-backup.sqlite3
```

Store backups encrypted outside the server and test restoration. Stop the app before restoring the database, preserve volume ownership (UID 10001), then restart it. Backups contain sensitive records and account hashes. Do not run `docker compose down -v` unless you intend to erase all volumes. Keep the secret key stable across restarts. Review dependency/security updates, regularly clear expired sessions with `python manage.py clearsessions`, and trim old login-attempt records per your retention policy.

## Scope and hosting

This release supports one organization, one application instance, list-based permissions, spreadsheet imports, private asset pictures, service records, and assignment history. It does not include SSO, MFA, email invitations, barcode scanning, or a tamper-proof audit store. Database administrators can modify stored audit data.
