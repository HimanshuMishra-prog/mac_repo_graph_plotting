from flask import Blueprint

from flaskr.routes.analyze_route import analyze_bp
from flaskr.routes.home_route import home_bp
from flaskr.routes.jobs_route import jobs_bp
from flaskr.routes.login_route import login_bp
from flaskr.routes.logout_route import logout_bp
from flaskr.routes.register_route import register_bp
from flaskr.routes.grafana_sso import grafana_sso

blueprints = [analyze_bp,home_bp,jobs_bp,login_bp,logout_bp,register_bp,grafana_sso]

