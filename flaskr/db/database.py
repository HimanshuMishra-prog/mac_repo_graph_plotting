from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_database():
    return db

