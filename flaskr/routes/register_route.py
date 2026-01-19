from flask import Blueprint, redirect, url_for, request,render_template ,flash
from flaskr.db.database_functions import get_user_by_username , register_user
from werkzeug.security import generate_password_hash

register_bp = Blueprint('register', __name__, template_folder='../templates')

@register_bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user= get_user_by_username(username)
        if user:
            flash("Username already taken!" , "error")
            return render_template("sign_up.html")
        elif username=="":
            flash("Username cannot be blank" , "error")
            return render_template("sign_up.html")
        elif password=="":
            flash("Password cannot be blank" , "error")
            return render_template("sign_up.html")
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = register_user(username= username, password= hashed_password)
        if not new_user:
            flash("Error creating new user")
        else :
            flash("New User Created! Please Log in" , "success")
            return redirect(url_for("login.login"))
    return render_template("sign_up.html")