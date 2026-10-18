#!/usr/bin/env python3
"""Configure and initialize Assetdesk on a conventional Python web host."""
import argparse
import json
import os
import secrets
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Configure an Assetdesk installation")
    parser.add_argument("--domain", required=True, help="Hostname only, for example assets.example.com")
    parser.add_argument("--database", help="SQLite database path (default: assets.sqlite3 in this folder)")
    parser.add_argument("--timezone", default="UTC", help="IANA time zone, for example Asia/Dhaka")
    parser.add_argument("--proxy", action="store_true", help="Trust X-Forwarded-Proto from a controlled reverse proxy")
    parser.add_argument("--force", action="store_true", help="Replace an existing private configuration")
    args = parser.parse_args()
    domain = args.domain.strip().lower().rstrip(".")
    if not domain or "://" in domain or "/" in domain or " " in domain:
        parser.error("--domain must be a hostname without a scheme, path, or port")
    root = Path(__file__).resolve().parent
    config = root / ".hosting.json"
    if config.exists() and not args.force:
        parser.error(f"{config} already exists; use --force only when intentionally replacing it")
    database = Path(args.database).expanduser().resolve() if args.database else root / "assets.sqlite3"
    values = {"SECRET_KEY": secrets.token_urlsafe(64), "DEBUG": "0", "ALLOWED_HOSTS": domain,
              "CSRF_TRUSTED_ORIGINS": f"https://{domain}", "DATABASE_PATH": str(database),
              "TIME_ZONE": args.timezone, "TRUST_PROXY": "1" if args.proxy else "0"}
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if args.force else os.O_EXCL)
    descriptor = os.open(config, flags, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        json.dump(values, handle, indent=2)
    os.chdir(root)
    from config.hosting import load_hosting_environment
    load_hosting_environment()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", interactive=False)
    call_command("collectstatic", interactive=False, verbosity=0)
    call_command("check", deploy=True)
    if database.exists(): os.chmod(database, 0o600)
    print("Assetdesk configured. Create an administrator with: python manage.py createsuperuser")


if __name__ == "__main__":
    main()
