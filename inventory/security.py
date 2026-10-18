import os
from ipaddress import ip_address

def client_ip(request):
    # TRUST_PROXY is safe only while the app is isolated behind our Caddy service.
    raw = request.META.get('REMOTE_ADDR','')
    if os.getenv('TRUST_PROXY','0') == '1':
        raw = request.META.get('HTTP_X_FORWARDED_FOR',raw)
    try:
        return str(ip_address(raw.strip()))
    except ValueError:
        return None
