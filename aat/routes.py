from . import app
from flask import render_template
from .decorators import admin_required, permission_required
from . import Permission
from .db_utils import get_all_assessment_marks, get_all_response_details


@app.route("/")
def index():
    return render_template("landing_page.html")


@app.route("/permissions")
@permission_required(Permission.WRITE_ASSESSMENT)
def for_lecturers_only():
    return "Permission works!"


@app.route("/assessment-marks")
def get_assessment_marks():
    results = get_all_assessment_marks()
    return render_template("db_utils/assessment-marks.html", results=results)


@app.route("/response-details")
def get_response_details():
    results = get_all_response_details()
    return render_template("db_utils/response-details.html", results=results)
