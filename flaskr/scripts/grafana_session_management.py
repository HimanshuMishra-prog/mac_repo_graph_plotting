import random
import time
import urllib
import requests
import base64
from flask import current_app
import base64
import requests
import logging

logger = logging.getLogger(__name__)

def create_grafana_user_if_not_exists(username):
    app_obj = current_app._get_current_object()
    grafana_host = app_obj.config.get("GRAFANA_API_HOST", "http://107.99.46.66:3000")
    
    try:
        headers = {
            'Authorization': f'Bearer {app_obj.config.get("GRAFANA_SERVICE_TOKEN", "glsa_P6EDMcKDKVpTrWqF63UlpaMt0q7pbRjg_c7acd895")}',
            'Content-Type': 'application/json'
        }
        
        check_url = f"{grafana_host}/api/org/users/lookup"
        response = requests.get(check_url, headers=headers, timeout=5)
        logger.info(f"User lookup response: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            user_exists = any(
                user.get('login', '').lower() == username.lower() 
                for user in users
            )
            
            if user_exists:
                logger.info(f"User {username} already exists in organization")
                return True
            else:
                logger.info(f"User {username} not found in organization, proceeding to create...")
                
        elif response.status_code == 403:
            logger.info(f"Service account lacks permission for org lookup: {response.text}")
        else:
            logger.info(f"User lookup failed: {response.status_code} - {response.text}")
        
        admin_user = app_obj.config.get("GRAFANA_ADMIN_USER", "admin")
        admin_pass = app_obj.config.get("GRAFANA_ADMIN_PASSWORD", "admin")
        
        admin_auth = base64.b64encode(f"{admin_user}:{admin_pass}".encode()).decode()
        
        create_headers = {
            'Authorization': f'Basic {admin_auth}',
            'Content-Type': 'application/json'
        }
        
        user_data = {
            "name": username,
            "email": f"{username}@samsung.com",
            "login": username,
            "password": username,
            "orgId": 1
        }
        
        create_url = f"{grafana_host}/api/admin/users"
        create_response = requests.post(create_url, 
                                     headers=create_headers, 
                                     json=user_data, 
                                     timeout=5)
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            logger.info(f"Successfully created user: {username} with ID: {response_data.get('id', 'unknown')}")
            return True
        elif create_response.status_code == 401 :
            logger.info("Authentication failed check admin credentials")
        else :
            logger.info("Failed to create user")
    except Exception as e:
        logger.error(f"Error wile createint user : {e}")

def silent_login(username):
    app_obj = current_app._get_current_object()
    grafana_host = app_obj.config.get("GRAFANA_API_HOST", "http://107.99.46.66:3000")
    
    try:
        logger.info(f"Logging out any existing user...")
        logout_response = requests.post(
            f"{grafana_host}/logout",
            timeout=3
        )
        logger.info(f"Logout status: {logout_response.status_code}")
        
        logger.info(f"Logging in as: {username}")
        login_data = {
            "user": username,
            "password": username
        }
        
        response = requests.post(
            f"{grafana_host}/login",
            json=login_data,
            timeout=5,
            allow_redirects=False
        )
        logger.info(f"Silent login response : {response.status_code} , {response.text}")
        if response.status_code == 200:
            logger.info(f"Successfully logged in user: {username}")
            return True
        else:
            logger.info(f"Login failed for {username}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Login error for {username}: {e}")
        return False
    
def make_grafana_url(filename, token, scenario,run_id):
    app_obj = current_app._get_current_object()
    grafana_host = app_obj.config.get("GRAFANA_HOST", "http://107.99.46.66:8080")
    ts = int(time.time() * 1000)
    session_id = f"{ts}_{random.randint(1000, 9999)}"
    dashboard_uid = "07102025-srib-mac-default"
    match scenario :
        case "4G_BASIC":
            dashboard_uid = "07102025-srib-mac-4g-scenario"
        case "4G_STATE_CHANGE":
            dashboard_uid = "07102025-srib-mac-4g-state-change"
        case "5G":
            dashboard_uid = "07102025-srib-mac-5g-scenario-v1"
        case _ :
            dashboard_uid = app_obj.config.get("GRAFANA_DASH_UID" , "07102025-srib-mac-default")
    grafana_url = (
        f"{grafana_host}/d/{dashboard_uid}"
        f"?var-filename={urllib.parse.quote(filename)}"
        f"&var-run_id={run_id}"
        f"&token={urllib.parse.quote(token)}"
        f"&_ts={ts}"
        f"&refresh=dashboard"        
        f"&kiosk=tv"                
        f"&__session={session_id}"
    )
    return grafana_url