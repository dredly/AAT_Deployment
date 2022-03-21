from . import auth
from .. import db
from ..models import User
from .forms import RegistrationForm
from flask import redirect, render_template, request, url_for 
from ..decorators import admin_required, permission_required 


@auth.route("/login")
def login():
    return render_template("login.html", title="Login")


@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST': 
        if form.admin.data == True: 
            teacher = User(name=form.name.data, password=form.password.data, is_admin=True)
            db.session.add(teacher)
            db.session.commit()
        elif form.admin.data == False: 
            student = User(name=form.name.data, password=form.password.data, is_admin=False)
            db.session.add(student)
            db.session.commit()
        return redirect(url_for('auth.registered'))
    return render_template("register.html", title="Register", form=form)

@auth.route("/registered")
def registered(): 
    return render_template("registered.html", title="Thanks!")
