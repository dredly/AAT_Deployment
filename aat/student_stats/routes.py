from . import student_stats
from flask_login import current_user
from flask import render_template, redirect, url_for
from sqlalchemy import func
from io import StringIO
import csv
from flask import make_response

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
    # How many marks
    # Each question
    return render_template(
        "student_stats_home.html",
        overall_results=overall_results,
        module_dict=module_dict,
    )


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
