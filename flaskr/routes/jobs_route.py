import random
from flask import Blueprint, render_template,request,flash, redirect , url_for,current_app
from flask_login import login_required, current_user
import os
from flaskr.scripts.replay_worker import start_replay_thread
from flaskr.routes.grafana_sso import make_signed_token
import time
from flaskr.scripts.grafana_session_management import create_grafana_user_if_not_exists,make_grafana_url
from flaskr.db.database_functions import get_logs_by_sno_username, delete_logs, get_logs_by_username
import logging

UPLOAD_FOLDER = 'uploads'
jobs_bp = Blueprint('jobs', __name__, template_folder='../templates')
logger = logging.getLogger(__name__)

@jobs_bp.route('/jobs',methods=['POST','GET'])
@login_required
def jobs():
    if request.method == 'POST':
        if 'delete' in request.form:
            log_file_id = request.form.get('SNo')
            log_file_owner = request.form.get('username')
            log_file_name = delete_logs(sno = log_file_id, username= log_file_owner)
            if log_file_name is not None and log_file_name!= "":
                try :
                    file_path = os.path.join(UPLOAD_FOLDER,log_file_name)
                    os.remove(file_path)
                    flash("Log file successfully deleted", "success")
                except Exception as e:
                    flash(f"Error.Deleting file: {str(e)}", "error")
                    logger.error(f"Error.Deleting file: {str(e)}")
            else :
                flash("Error. Record not found", "error")
            return redirect(url_for("jobs.jobs"))    
        elif 'analyze' in request.form:
            log_file_id = request.form.get('SNo')
            log_file_owner = request.form.get('username')
            scenario = request.form.get('scenario')
            log_file = get_logs_by_sno_username(sno=log_file_id, username=log_file_owner)
            if log_file is None:
                flash("Error. Record not found", "error")
                return redirect(url_for("jobs.jobs"))
            file_path = log_file.filelocation if getattr(log_file, "FileLocation", None) else os.path.join(UPLOAD_FOLDER, log_file.filename)
            if not os.path.exists(file_path):
                flash("Error. File not found on disk", "error")
                return redirect(url_for("jobs.jobs"))
            app_obj = current_app._get_current_object()
            loki_url = app_obj.config.get("LOKI_PUSH_URL", "http://127.0.0.1:3100")
            batch_size = int(app_obj.config.get("REPLAY_BATCH_SIZE", 2000))
            replay_delay = float(request.form.get("replay_delay", app_obj.config.get("REPLAY_DELAY", 0)))
            requests_per_second = app_obj.config.get("LOKI_REQUESTS_PER_SECOND", 5)
       
            create_grafana_user_if_not_exists(current_user.username)   
                  
            try:
                run_id = random.randint(10000,99999)
                start_replay_thread(
                    app=app_obj,
                    log_sno=log_file.sno,
                    username=current_user.username,
                    file_path=file_path,
                    filename=log_file.filename,
                    loki_url=loki_url,
                    batch_size=batch_size,
                    replay_delay=replay_delay,
                    scenario = scenario if scenario else "4G_BASIC",
                    run_id = run_id,
                    tenant=None,
                    requests_per_second=requests_per_second
                )
                token = make_signed_token(current_user.username)         
                
                grafana_url = make_grafana_url(log_file.filename,token,scenario,run_id)
                return render_template("grafana_open.html", url=grafana_url, return_url=url_for("jobs.jobs"))
            except Exception as e:
                flash(f"Failed to start replay/ Open Graph: {e}", "error")
            return redirect(url_for("jobs.jobs"))
    all_files = get_logs_by_username(current_user.username)
    all_files.reverse()
    return render_template("jobs.html", all_jobs = all_files)
