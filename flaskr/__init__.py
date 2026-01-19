from flask import Flask
from flaskr.routes import blueprints 
from .config import Config
from .db.database import create_database
from flask_migrate import Migrate
from .db.database_functions import get_user_by_id
from flask_login import LoginManager
from prometheus_flask_exporter import PrometheusMetrics
import logging
from .logger import init_logging

migrate = Migrate()
login_manager = LoginManager()
log = logging.getLogger('werkzeug')

class NoPrometheus(logging.Filter):
    def filter(self, record):
        return "/metrics" not in record.getMessage()

log.addFilter(NoPrometheus())  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_logging(app) 

    db = create_database()
    db.init_app(app)

    metrics = PrometheusMetrics(app , path = '/metrics') 

    migrate.init_app(app, db, directory='migrations')

    with app.app_context():
        from .db.models import User
        db.create_all()
        
        # Configure SQLite for better concurrency using connection
        if app.config.get('SQLITE_ENABLE_WAL'):
            with db.engine.connect() as conn:
                conn.execute(db.text("PRAGMA journal_mode=WAL"))
        if app.config.get('SQLITE_SYNCHRONOUS'):
            with db.engine.connect() as conn:
                conn.execute(db.text(f"PRAGMA synchronous={app.config['SQLITE_SYNCHRONOUS']}"))
        if app.config.get('SQLITE_CACHE_SIZE'):
            with db.engine.connect() as conn:
                conn.execute(db.text(f"PRAGMA cache_size={app.config['SQLITE_CACHE_SIZE']}"))
        if app.config.get('SQLITE_TEMP_STORE'):
            with db.engine.connect() as conn:
                conn.execute(db.text(f"PRAGMA temp_store={app.config['SQLITE_TEMP_STORE']}"))

    login_manager.init_app(app)
    login_manager.login_view = "login"

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    return app
