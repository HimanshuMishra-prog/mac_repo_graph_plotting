from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required,logout_user

logout_bp = Blueprint('logout', __name__, template_folder='../templates')

@logout_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("User Logged out Successfully" , "success")
    return redirect(url_for("home.home"))