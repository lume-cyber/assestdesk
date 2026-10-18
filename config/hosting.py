"""Load an optional private cPanel configuration, preserving process overrides."""
import json
import os
from pathlib import Path

def load_hosting_environment():
    config_path = Path(__file__).resolve().parent.parent / '.hosting.json'
    if config_path.exists():
        values = json.loads(config_path.read_text())
        allowed = {'SECRET_KEY','DEBUG','ALLOWED_HOSTS','CSRF_TRUSTED_ORIGINS','DATABASE_PATH','TIME_ZONE','TRUST_PROXY'}
        for name, value in values.items():
            if name in allowed:
                os.environ.setdefault(name, str(value))
