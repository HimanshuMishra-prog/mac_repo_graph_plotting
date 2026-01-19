from flask import render_template, request, redirect, url_for, Blueprint , flash
from flaskr.db.database_functions import register_logs,delete_logs
import os
from flask_login import login_required, current_user
from datetime import datetime
import logging

UPLOAD_FOLDER = 'uploads'

logger = logging.getLogger(__name__)
analyze_bp = Blueprint('analyze', __name__, template_folder='../templates')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@analyze_bp.route("/analyze", methods=['GET','POST'])
@login_required
def analyze():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if len(files):
            job_type = request.form['type']
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M")
            name = None
            file_names = [f.filename for f in files if f.filename]
            name = ", ".join(file_names)
            username = current_user.username
            for file in files:
                try :
                    fname = file.filename
                    file_path = os.path.join(UPLOAD_FOLDER,fname)
                    logFile = register_logs(username = username, filename = fname, file_path = file_path, time = formatted_time)
                    try:
                        file.save(file_path)
                    except Exception as e:
                        delete_logs(sno = logFile.sno, username= logFile.username)
                        logger.error(f"Error saving file {fname} for user : {username}")
                        flash(flash(f"Error saving file, Try changing filename/size" , "error"))
                        return redirect(url_for('analyze.analyze'))
                except Exception as e:
                    logger.error(f"Error saving file {fname} for user : {username}")
                    flash(f"Error saving file, Try changing filename/size" , "error")
                    return redirect(url_for('analyze.analyze'))
            flash("File Uploaded Successfully!" , "success")
            return redirect(url_for('jobs.jobs'))
    return render_template("analyze.html")