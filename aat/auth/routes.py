from . import auth
from ..models import User 
from flask import render_template


@auth.route("/login")
def login():
    return render_template("login.html", title="Login")


@auth.route("/register")
def register():
    return render_template("register.html", title="Register")
