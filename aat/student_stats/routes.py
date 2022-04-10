from . import student_stats
from flask_login import current_user
from flask import render_template, redirect, url_for
from sqlalchemy import func
from io import StringIO
import csv, pprint, json
from flask import make_response
from werkzeug.exceptions import NotFound
from .. import db

# MODELS
from ..models import *

# Database Util Functions
from ..db_utils import *

###############
# COURSE VIEW #
###############
@student_stats.route("/")
def course_view():
    ## VALIDATION ##
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    ## RETURN ##
    return render_template(
        "1_student_stats_course_view.html",
    )


###############
# MODULE VIEW #
###############
@student_stats.route("/module/")
@student_stats.route("/module/<int:module_id>")
def module_view(module_id=0):
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    # Module Error Handling
    if Module.query.filter_by(module_id=module_id).first() is None:
        return redirect(url_for("student_stats.module_not_found", module_id=module_id))

    ## RETURN ##
    return render_template(
        "2_student_stats_module_view.html",
    )


###################
# ASSESSMENT VIEW #
###################
@student_stats.route("/assessment/")
@student_stats.route("/assessment/<int:assessment_id>")
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

    # Bar Chart Data
    barChartData = []
    barChartColor = []
    barChartPass = []
    barChartLabel = []
    pass_color = "54, 162, 235, 0.8"
    fail_color = "255, 99, 132, 0.8"
    total_marks_possible = a.get_total_marks_possible()
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

    ## RETURN ##
    return render_template(
        "3_student_stats_assessment_view.html",
        a=a,
        data_for_bar_chart=data_for_bar_chart,
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
            "Assessment": response.assessment,
            "Question": response.question,
            "Response": response.response_content,
            "Correct": response.is_correct,
            "Marks": response.question.num_of_marks,
        }
        for response in current_user.t2_responses
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


@student_stats.route("/test")
def test():
    query = Assessment.query.all()
    for q in query:
        print(
            f"Initial list: {q.get_dict_of_tags_and_answers(current_user.id, attempt_number=10)}"
        )
    return "."
