from . import app
from flask import render_template
from .decorators import admin_required, permission_required
from . import Permission


@app.route("/")
def index():
    return render_template("landing_page.html")


@app.route("/permissions")
@permission_required(Permission.WRITE_ASSESSMENT)
def for_lecturers_only():
    return "Permission works!"
