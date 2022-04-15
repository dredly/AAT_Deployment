from . import student_stats
from flask_login import current_user
from flask import render_template, redirect, url_for, request, jsonify
from io import StringIO
import csv, json
from flask import make_response
from .. import db

# MODELS
from ..models import *

# Database Util Functions
from ..db_utils import *

###############
# COURSE VIEW #
###############
@student_stats.route("/", methods=["POST", "GET"])
def course_view():
    ## VALIDATION ##
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    ## RETURN ##

    c = Course.query.first()
    return render_template("1_student_stats_course_view.html", c=c)


@student_stats.route("/course-analysis/", methods=["POST", "GET"])
def course_analysis():
    summative_only = None
    formative_only = None
    hsa_only = None

    if request.method == "POST":
        analysis_filter = request.form["analysis_filter"]
        if analysis_filter == "summative":
            summative_only = True
        elif analysis_filter == "formative":
            formative_only = True
        hsa_only = True if request.form.get("hsa_only") == "on" else None

    c = Course.query.first()
    return render_template(
        "course_analysis.html",
        c=c,
        summative_only=summative_only,
        formative_only=formative_only,
        hsa_only=hsa_only,
    )


###############
# MODULE VIEW #
###############
@student_stats.route("/module/", methods=["POST", "GET"])
@student_stats.route("/module/<int:module_id>", methods=["POST", "GET"])
def module_view(module_id=0):
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    m = Module.query.filter_by(module_id=module_id).first()

    summative_only = None
    formative_only = None

    if request.method == "POST":
        analysis_filter = request.form["analysis_filter"]
        if analysis_filter == "summative":
            summative_only = True
        elif analysis_filter == "formative":
            formative_only = True

    # Module Error Handling
    if m is None:
        return redirect(url_for("student_stats.module_not_found", module_id=module_id))

    # REDIRECT IF USER HASN'T ATTEMPTED YET:
    if m.get_status(current_user.id) == "unattempted":
        return render_template(
            "no_assessments_answered.html",
        )

    ## RETURN ##
    return render_template(
        "2_student_stats_module_view.html",
        m=m,
        summative_only=summative_only,
        formative_only=formative_only,
    )


@student_stats.route("/module-analysis/<int:module_id>", methods=["POST", "GET"])
def module_analysis(module_id):
    m = Module.query.filter_by(module_id=module_id).first()

    summative_only = None
    formative_only = None
    hsa_only = None

    if request.method == "POST":
        analysis_filter = request.form["analysis_filter"]
        if analysis_filter == "summative":
            summative_only = True
        elif analysis_filter == "formative":
            formative_only = True
        hsa_only = True if request.form.get("hsa_only") == "on" else None

    return render_template(
        "module_analysis.html",
        m=m,
        summative_only=summative_only,
        formative_only=formative_only,
        hsa_only=hsa_only,
    )


###################
# ASSESSMENT VIEW #
###################
@student_stats.route("/assessment/", methods=["POST", "GET"])
@student_stats.route("/assessment/<int:assessment_id>", methods=["POST", "GET"])
def assessment_view(assessment_id=0):
    ## VALIDATION ##
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    a = Assessment.query.filter_by(assessment_id=assessment_id).first()

    # Assessment Error Handling
    if not a:
        return redirect(
            url_for("student_stats.module_not_found", assessment_id=assessment_id)
        )

    # Bar Chart Data (should eventually be able to do that in-template)
    barChartData = []
    barChartColor = []
    barChartPass = []
    barChartLabel = []
    pass_color = "54, 162, 235, 0.8"
    fail_color = "255, 99, 132, 0.8"
    total_marks_possible = a.get_total_marks_possible()
    if a.get_list_of_attempts_made(current_user.id):
        for attempt in a.get_list_of_attempts_made(current_user.id):
            marks = a.get_marks_for_user_and_assessment(current_user.id)[attempt]
            pass_mark = total_marks_possible / 2
            barChartData.append(marks)
            barChartPass.append(pass_mark)
            barChartLabel.append(attempt)
            barChartColor.append(
                pass_color
            ) if marks >= pass_mark else barChartColor.append(fail_color)

    data_for_bar_chart = {
        "barChartData": barChartData,
        "barChartColor": barChartColor,
        "barChartPass": barChartPass,
        "barChartLabel": barChartLabel,
    }

    ## RETURNS ##

    # REDIRECT IF USER HASN'T ATTEMPTED YET:
    if a.get_status(current_user.id) == "unattempted":
        return render_template(
            "no_questions_answered.html",
        )

    # MAIN #
    return render_template(
        "3_student_stats_assessment_view.html",
        a=a,
        data_for_bar_chart=data_for_bar_chart,
    )


@student_stats.route(
    "/assessment-analysis/<int:assessment_id>", methods=["POST", "GET"]
)
def assessment_analysis(assessment_id):
    a = Assessment.query.filter_by(assessment_id=assessment_id).first()

    summative_only = None
    formative_only = None
    hsa_only = None  # hsa = "highest scoring attempt"

    if request.method == "POST":
        analysis_filter = request.form["analysis_filter"]
        if analysis_filter == "summative":
            summative_only = True
        elif analysis_filter == "formative":
            formative_only = True
        hsa_only = True if request.form.get("hsa_only") == "on" else None

    return render_template(
        "assessment_analysis.html",
        a=a,
        summative_only=summative_only,
        formative_only=formative_only,
        hsa_only=hsa_only,
    )


######################
# EXCEPTION HANDLING #
######################
@student_stats.route("/module/not-found/<int:module_id>")
def module_not_found(module_id):
    # Make list of modules the logged in user does take:
    return render_template(
        "exception_handling/module_not_found.html",
        module_id=module_id,
        list_of_modules=sorted(
            list(
                set(
                    [
                        response.assessment.module
                        for response in current_user.t2_responses
                    ]
                )
            ),
            key=lambda x: x.module_id,
            reverse=False,
        ),
    )


################
# DOWNLOAD CSV #
################

# Download a .csv
# https://stackoverflow.com/questions/26997679/writing-a-csv-from-flask-framework

# https://www.programcreek.com/python/example/3190/csv.DictWriter
@student_stats.route("/download")
def download():
    rows = [
        {
            "Module": response.assessment.module,
            "Assessment": response.assessment,
            "Question": response.question,
            "Response": response.get_answer_given(),
            "Correct": response.is_correct,
            "Marks": response.question.num_of_marks,
            "Feedback": response.get_feedback(),
            "Feedforward": response.get_feedforward(),
        }
        # TODO: change this to be all responses
        for responses in [current_user.t1_responses, current_user.t2_responses]
        for response in responses
    ]
    string_io = StringIO()
    csv_writer = csv.DictWriter(string_io, rows[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(rows)
    output = make_response(string_io.getvalue())
    output.headers[
        "Content-Disposition"
    ] = f"attachment; filename={current_user.name}-aat-export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
