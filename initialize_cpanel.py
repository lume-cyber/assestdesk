"""Compatibility entry point. New installations should run configure.py."""
raise SystemExit(
    "Run: python configure.py --domain YOUR-DOMAIN --timezone YOUR-TIMEZONE\n"
    "Example: python configure.py --domain assets.example.com --timezone UTC"
)
