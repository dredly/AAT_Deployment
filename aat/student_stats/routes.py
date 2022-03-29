from . import student_stats
from flask_login import current_user
from flask import render_template, redirect, url_for
from sqlalchemy import func
from io import StringIO
import csv
from flask import make_response
from werkzeug.exceptions import NotFound

# MODELS
from ..models import (
    Module,
    Assessment,
    QuestionT1,
    QuestionT2,
    Option,
    User,
    ResponseT2,
)

###############
# COURSE VIEW #
###############
@student_stats.route("/")
def course_view():
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    # GET SUM OF QUESTIONS FOR EACH ASSESSMENT
    assessment_marks_dict = {}

    for response in current_user.t2_responses:
        if response.assessment not in assessment_marks_dict:
            assessment_marks_dict[response.assessment] = {
                "marks_awarded": response.question.num_of_marks
                if response.is_correct
                else 0,
                "marks_possible": response.question.num_of_marks,
            }
        else:
            assessment_marks_dict[response.assessment]["marks_awarded"] += (
                response.question.num_of_marks if response.is_correct else 0
            )
            assessment_marks_dict[response.assessment][
                "marks_possible"
            ] += response.question.num_of_marks

    # ADD THAT TO THE MODULE DICT
    module_dict = {}

    for module in Module.query.all():
        for assessment, data in assessment_marks_dict.items():
            if assessment.module_id == module.module_id:
                module_dict[module] = {assessment: data}

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for module in module_dict:
        for assessment, data in assessment_marks_dict.items():
            sum_of_marks_awarded += data["marks_awarded"]
            sum_of_marks_possible += data["marks_possible"]

    if sum_of_marks_possible == 0:
        return render_template("no_questions_answered.html")

    overall_results = {
        "sum_of_marks_awarded": sum_of_marks_awarded,
        "sum_of_marks_possible": sum_of_marks_possible,
    }

    return render_template(
        "student_stats_course_view.html",
        overall_results=overall_results,
        module_dict=module_dict,
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

    module_details = {
        "module_id": module_id,
        "module_name": Module.query.filter_by(module_id=module_id).first(),
    }

    # GET SUM OF QUESTIONS FOR EACH ASSESSMENT
    assessment_marks_dict = {}

    for response in current_user.t2_responses:
        if response.assessment.module_id == module_id:
            if response.assessment not in assessment_marks_dict:
                assessment_marks_dict[response.assessment] = {
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
            else:
                assessment_marks_dict[response.assessment]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks_dict[response.assessment][
                    "marks_possible"
                ] += response.question.num_of_marks

    # ADD THAT TO THE MODULE DICT
    module_dict = {module_id: assessment_marks_dict}

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for module in module_dict:
        for assessment, data in assessment_marks_dict.items():
            sum_of_marks_awarded += data["marks_awarded"]
            sum_of_marks_possible += data["marks_possible"]

    if sum_of_marks_possible == 0:
        return render_template("no_questions_answered.html")

    overall_results = {
        "sum_of_marks_awarded": sum_of_marks_awarded,
        "sum_of_marks_possible": sum_of_marks_possible,
    }

    return render_template(
        "student_stats_module_view.html",
        overall_results=overall_results,
        module_dict=module_dict,
        module_id=module_id,
    )


###################
# ASSESSMENT VIEW #
###################


@student_stats.route("/assessment/")
@student_stats.route("/assessment/<int:assessment_id>")
def assessment_view(assessment_id=0):
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    # Assessment Error Handling
    if Assessment.query.filter_by(assessment_id=assessment_id).first() is None:
        return redirect(
            url_for("student_stats.module_not_found", assessment_id=assessment_id)
        )

    assessment_details = {
        "assessment_id": assessment_id,
        "assessment_name": Assessment.query.filter_by(
            assessment_id=assessment_id
        ).first(),
    }

    # GET SUM OF QUESTIONS FOR EACH ASSESSMENT
    assessment_marks_dict = {}

    for response in current_user.t2_responses:
        if response.assessment.assessment_id == assessment_id:
            if response.assessment not in assessment_marks_dict:
                assessment_marks_dict[response.assessment] = {
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
            else:
                assessment_marks_dict[response.assessment]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks_dict[response.assessment][
                    "marks_possible"
                ] += response.question.num_of_marks

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for assessment, data in assessment_marks_dict.items():
        sum_of_marks_awarded += data["marks_awarded"]
        sum_of_marks_possible += data["marks_possible"]

    if sum_of_marks_possible == 0:
        return render_template("no_questions_answered.html")

    overall_results = {
        "sum_of_marks_awarded": sum_of_marks_awarded,
        "sum_of_marks_possible": sum_of_marks_possible,
    }

    return render_template(
        "student_stats_assessment_view.html",
        overall_results=overall_results,
        assessment_marks_dict=assessment_marks_dict,
        assessment_id=assessment_id,
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


@student_stats.route("/assessment/not-found/<int:assessment_id>")
def assessment_not_found(assessment_id):
    return "TODO"


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
