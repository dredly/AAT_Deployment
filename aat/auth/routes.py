from . import auth
from flask import render_template


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/register")
def register():
    return render_template("register.html")
