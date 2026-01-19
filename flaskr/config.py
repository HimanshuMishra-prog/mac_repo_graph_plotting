class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///default.db'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'timeout': 30,
            'check_same_thread': False
        }
    }
    SQLITE_ENABLE_WAL = True
    SQLITE_SYNCHRONOUS = 'NORMAL'
    SQLITE_CACHE_SIZE = 2000
    SQLITE_TEMP_STORE = 'MEMORY'
    
    #FOR GRAFANA
    AUTH_PROXY_SECRET = "secret_key"
    GRAFANA_HOST = "http://107.99.46.66:8080"
    GRAFANA_API_HOST = "http://107.99.46.66:3000"
    GRAFANA_DASH_UID = "07102025-srib-mac-default"
    GRAFANA_LOGIN_EXPIRY = 100000000000000
    GRAFANA_SERVICE_TOKEN = "glsa_P6EDMcKDKVpTrWqF63UlpaMt0q7pbRjg_c7acd895" 
    GRAFANA_ADMIN_USER = "admin" 
    GRAFANA_ADMIN_PASSWORD = "admin" 
    
    #LOKi
    REPLAY_BATCH_SIZE = "1000"
    LOKI_REQUESTS_PER_SECOND = 10
    REPLAY_DELAY=0.001
