import time
import hmac
import hashlib
import base64
import html 
from urllib.parse import parse_qs, urlparse
from flask import current_app, request, Response, Blueprint
import logging

grafana_sso = Blueprint('grafana_auth', __name__, template_folder='../templates')
logger = logging.getLogger(__name__)

def make_signed_token(username: str, expiry_seconds: int = 100000) -> str:
    secret = current_app.config.get("AUTH_PROXY_SECRET")
    if not secret:
        raise RuntimeError("AUTH_PROXY_SECRET not set in config")
    expiry = int(time.time()) + int(expiry_seconds)
    payload = f"{username}|{expiry}"
    mac = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token_raw = f"{payload}|{mac}"
    token_b64 = base64.urlsafe_b64encode(token_raw.encode()).decode()
    return token_b64

def verify_signed_token(token_b64: str):
    secret = current_app.config.get("AUTH_PROXY_SECRET")
    if not secret:
        return None
    try:
        token_raw = base64.urlsafe_b64decode(token_b64.encode()).decode()
        username, expiry_s, mac = token_raw.rsplit("|", 2)
        expiry = int(expiry_s)
    except Exception:
        return None
    if expiry < int(time.time()):
        logger.error("expiry failed")
        return None
    expected_mac = hmac.new(secret.encode(), f"{username}|{expiry}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_mac, mac):
        return None
    return username

@grafana_sso.route("/grafana_auth")
def grafana_auth():
    original_uri = request.headers.get("X-Original-URI")
    token = None 
    if original_uri:
        decoded_uri = html.unescape(original_uri)   
        parsed = urlparse(decoded_uri)
        query_params = parse_qs(parsed.query)
        token = query_params.get('token', [None])[0]  
    if not token:
        logger.error("grafana_auth -> no token provided")
        return Response("no token", status=401)       
    user = verify_signed_token(token)
    if not user:
        logger.error("grafana_auth -> invalid token")
        return Response("invalid token", status=401)
    resp = Response("ok", status=200)
    resp.headers["X-Auth-User"] = user
    return resp