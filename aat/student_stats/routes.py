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
    assessment_marks = {}

    ## T1_responses
    for response in current_user.t1_responses:
        if response.assessment not in assessment_marks:
            assessment_marks[response.assessment] = {
                "marks_awarded": response.question.num_of_marks
                if response.is_correct
                else 0,
                "marks_possible": response.question.num_of_marks,
            }
        else:
            assessment_marks[response.assessment]["marks_awarded"] += (
                response.question.num_of_marks if response.is_correct else 0
            )
            assessment_marks[response.assessment][
                "marks_possible"
            ] += response.question.num_of_marks

    ## T2_responses
    for response in current_user.t2_responses:
        if response.assessment not in assessment_marks:
            assessment_marks[response.assessment] = {
                "marks_awarded": response.question.num_of_marks
                if response.is_correct
                else 0,
                "marks_possible": response.question.num_of_marks,
            }
        else:
            assessment_marks[response.assessment]["marks_awarded"] += (
                response.question.num_of_marks if response.is_correct else 0
            )
            assessment_marks[response.assessment][
                "marks_possible"
            ] += response.question.num_of_marks

    # ADD THAT TO THE MODULE DICT
    module_dict = {}

    for module in Module.query.all():
        for assessment, data in assessment_marks.items():
            if assessment.module_id == module.module_id:
                if module not in module_dict:
                    module_dict[module] = {assessment: data}
                else:
                    module_dict[module][assessment] = data

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for module in module_dict:
        for assessment, data in assessment_marks.items():
            sum_of_marks_awarded += data["marks_awarded"]
            sum_of_marks_possible += data["marks_possible"]
            # module_dict[module]["marks_awarded"] += data["marks_awarded"]
            # module_dict[module]["marks_possible"] += data["marks_possible"]

    if sum_of_marks_possible == 0:
        return render_template("no_questions_answered.html")

    overall_results = {
        "sum_of_marks_awarded": sum_of_marks_awarded,
        "sum_of_marks_possible": sum_of_marks_possible,
    }

    module_totals = {}

    for module, module_details in module_dict.items():
        module_totals[module.title] = {"marks_awarded": 0, "marks_possible": 0}
        for assessment, assessment_details in module_details.items():
            module_totals[module.title]["marks_awarded"] += assessment_details[
                "marks_awarded"
            ]
            module_totals[module.title]["marks_possible"] += assessment_details[
                "marks_possible"
            ]

    print(f"{module_totals=}")

    return render_template(
        "student_stats_course_view.html",
        overall_results=overall_results,
        module_dict=module_dict,
        module_totals=module_totals,
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
    assessment_marks = {}

    # T1_RESPONSES
    for response in current_user.t1_responses:
        if response.assessment.module_id == module_id:
            if response.assessment not in assessment_marks:
                assessment_marks[response.assessment] = {
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
            else:
                assessment_marks[response.assessment]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks[response.assessment][
                    "marks_possible"
                ] += response.question.num_of_marks

    # T2_RESPONSES
    for response in current_user.t2_responses:
        if response.assessment.module_id == module_id:
            if response.assessment not in assessment_marks:
                assessment_marks[response.assessment] = {
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
            else:
                assessment_marks[response.assessment]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks[response.assessment][
                    "marks_possible"
                ] += response.question.num_of_marks

    # ADD THAT TO THE MODULE DICT
    module_dict = {module_id: assessment_marks}

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for module in module_dict:
        for assessment, data in assessment_marks.items():
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
        module_details=module_details,
        module_dict=module_dict,
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

    module_id = assessment_details["assessment_name"].module_id

    # GET SUM OF QUESTIONS FOR EACH ASSESSMENT
    assessment_marks = {}

    # T1_RESPONSES
    for response in current_user.t1_responses:
        if response.assessment.assessment_id == assessment_id:
            if response.question not in assessment_marks:
                assessment_marks[response.question] = {
                    "answer_given": response.chosen_option,
                    "is_correct": response.is_correct,
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
                # Check what correct answer was
                for option in Option.query.filter_by(
                    q_t1_id=response.question.q_t1_id
                ).all():
                    if option.is_correct:
                        assessment_marks[response.question][
                            "correct_answer"
                        ] = option.option_text
                # Check what feedback was given
                if response.is_correct:
                    assessment_marks[response.question][
                        "feedback_given"
                    ] = response.question.feedback_if_correct
                else:
                    assessment_marks[response.question][
                        "feedback_given"
                    ] = response.question.feedback_if_wrong
            else:
                # Rich: Unsure this step happens at a question level
                assessment_marks[response.question]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks[response.question][
                    "marks_possible"
                ] += response.question.num_of_marks

    # T2_RESPONSES
    for response in current_user.t2_responses:
        if response.assessment.assessment_id == assessment_id:
            if response.question not in assessment_marks:
                assessment_marks[response.question] = {
                    "answer_given": response.response_content,
                    "correct_answer": response.question.correct_answer,
                    "is_correct": response.is_correct,
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
                print(assessment_marks)
                # Feedback given:
                if response.is_correct:
                    assessment_marks[response.question][
                        "feedback_given"
                    ] = response.question.feedback_if_correct
                else:
                    assessment_marks[response.question][
                        "feedback_given"
                    ] = response.question.feedback_if_wrong
            else:
                # Rich: Unsure this step happens at a question level
                assessment_marks[response.question]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks[response.question][
                    "marks_possible"
                ] += response.question.num_of_marks

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for assessment, data in assessment_marks.items():
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
        module_id=module_id,
        assessment_details=assessment_details,
        assessment_marks=assessment_marks,
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
