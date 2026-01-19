import logging
import sys
from flask import Flask

def init_logging(app : Flask):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(fmt = '%(asctime)s | %(name)s | %(levelname)s | %(threadName)s | %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    
    if not root_logger.handlers :
        root_logger.addHandler(handler)
    
    app.logger.handler = root_logger.handlers
    app.logger.setLevel(logging.INFO)
    app.logger.info("Logging initialized")
