from flask import Blueprint, render_template, request, redirect, url_for , flash
from werkzeug.security import check_password_hash
from flaskr.db.database_functions import get_user_by_username
from flask_login import login_user

login_bp = Blueprint('login', __name__, template_folder='../templates')

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user_by_username(username=username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("User Logged In successfully" , "success")
            return redirect(url_for('analyze.analyze'))
        else:
            flash("Invalid username or password" , "error")
            return redirect(url_for('login.login'))
    return render_template("login.html")