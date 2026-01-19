from .database import create_database
from flask_login import UserMixin
import datetime

db = create_database()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    
    
class Logs(db.Model):
    sno = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement=True) 
    username = db.Column(db.String(250), nullable=False)
    filename = db.Column(db.String(50), nullable = False, server_default = 'default_value', index = True)
    time = db.Column(db.String(100), nullable=True)
    filelocation = db.Column(db.String(500), nullable = False)
    __table_args__ = (db.UniqueConstraint('username', 'filename', name='_user_filename_uc'),)

class Metadata(db.Model):
    sno = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement=True)
    username = db.Column(db.String(250), nullable=False, index= True)
    filename = db.Column(db.String(50), nullable = False, server_default = 'default_value', index = True)
    parsing_tag = db.Column(db.String(100), nullable= False)
    sector = db.Column(db.Integer)
    ue_id = db.Column(db.Integer)
    malperforming = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())