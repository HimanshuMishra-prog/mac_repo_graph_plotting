import logging
from .models import db, Logs, User, Metadata
from sqlalchemy.exc import IntegrityError, OperationalError
import datetime

logger = logging.getLogger(__name__)

def get_logs_by_sno_username(sno, username):
    return Logs.query.filter_by(sno=sno, username=username).first()

def get_logs_by_username(username):
    return Logs.query.filter_by(username=username).order_by(Logs.time.asc()).all()

def register_logs(username , filename , file_path , time) :
    logFile =  Logs(username = username, filename = filename, filelocation = file_path, time = time)
    try :
        db.session.add(logFile)
        db.session.commit()
        return logFile
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"DB Integrity error on log create: {e}")
        return None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected DB error on log create : {e}")
        return None

def delete_logs(sno, username):
    log_file = Logs.query.filter_by(sno=sno, username=username).first()
    if log_file is None:
       logger.error("Delete failed : Log not found for sno : {sno} and username : {username}") 
       return None
    try :
        db.session.delete(log_file)
        db.session.commit()
        return log_file.filename
    except Exception as e :
        db.session.rollback()
        logger.error(f"Unexpected DB error on log delete : {e}" )
        return None 

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def register_user(username , password) :
    new_user = User(username=username, password=password)
    try :
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"DB Integrity error on user register: {e}")
        return None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected DB error on user register : {e}")
        return None

def get_user_by_id(user_id):
    return User.query.get(user_id)

def save_metadata_to_db(username, filename , metadata_dict):
    metadata_objects = []
    updates_needed = []
    time = datetime.datetime.now()
    logger.info("Saving metadata to db...")
    for (tag, sector, ue_id), is_malperforming in metadata_dict.items():
        # exists = Metadata.query.filter_by(
        #     username = username,
        #     filename = filename,
        #     parsing_tag = tag,
        #     sector = sector,
        #     ue_id = ue_id
        # ).first()
        # if exists and is_malperforming and not exists.malperforming:
        #     exists.malperforming = True 
        #     exists.time = time 
        #     updates_needed.append(exists)
        # else :
            metadata_obj = Metadata(
                username = username,
                filename = filename,
                parsing_tag= tag,
                sector= sector,
                ue_id= ue_id,
                malperforming = is_malperforming,
                created_at = time
            )
            metadata_objects.append(metadata_obj)
            logger.info("object added")
            
    if metadata_objects:
        logger.info("making the push")
        db.session.bulk_save_objects(metadata_objects)
        
    for obj in updates_needed:
        logger.info("making the updates")
        db.session.add(obj)
    
    try :
        logger.info("commiting")
        db.session.commit() 
        return True
    except Exception as e:
        logger.info("leaving")
        db.session.rollback()
        return False
