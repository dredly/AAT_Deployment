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
from ..db_utils import (
    get_all_assessment_marks,
    get_module_ids_with_details,
    get_all_response_details,
)

# Generic marks_dictionary
marks_dictionary = {"sum_of_marks_awarded": 0, "sum_of_marks_possible": 0}


@student_stats.route("/rich")
def rich():
    results = get_all_assessment_marks()
    return render_template("rich.html", results=results)


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
    ############################################
    # NEW VERSION
    ############################################
    ##################
    # db_utils calls #
    ##################
    all_assessment_marks = get_all_assessment_marks(highest_scoring_attempt_only=True)
    all_assessment_marks_student = get_all_assessment_marks(
        input_user_id=current_user.id, highest_scoring_attempt_only=True
    )
    module_ids_with_details = get_module_ids_with_details()

    # OVERALL RESULTS
    # - STUDENT
    overall_results_student = marks_dictionary.copy()

    for assessment_mark in all_assessment_marks_student:
        overall_results_student["sum_of_marks_awarded"] += assessment_mark[
            "correct_marks"
        ]
        overall_results_student["sum_of_marks_possible"] += assessment_mark[
            "possible_marks"
        ]

    list_of_assessments_completed_by_student = [
        item["assessment_id"] for item in all_assessment_marks_student
    ]

    # - COHORT
    overall_results_cohort = marks_dictionary.copy()
    for assessment_mark in all_assessment_marks:
        if assessment_mark["assessment_id"] in list_of_assessments_completed_by_student:
            # Filter out if the
            overall_results_cohort["sum_of_marks_awarded"] += assessment_mark[
                "correct_marks"
            ]
            overall_results_cohort["sum_of_marks_possible"] += assessment_mark[
                "possible_marks"
            ]

    # MODULE RESULTS
    # - STUDENT
    module_stats_student = {}
    for assessment_mark in all_assessment_marks_student:
        module_stats_student[assessment_mark["module_id"]] = {
            "marks_awarded": assessment_mark["correct_marks"],
            "marks_possible": assessment_mark["possible_marks"],
            "taken_by_student": True,
        }

    # - > ADD MODULE STATS
    for module in module_ids_with_details:
        if module in module_stats_student:
            module_stats_student[module]["module_title"] = module_ids_with_details[
                module
            ]["module_title"]
            module_stats_student[module][
                "total_assessment_credits"
            ] = module_ids_with_details[module]["total_assessment_credits"]
            module_stats_student[module][
                "total_module_credits"
            ] = module_ids_with_details[module]["total_module_credits"]
        else:
            module_stats_student[module] = {
                "module_title": module_ids_with_details[module]["module_title"],
                "marks_awarded": 0,
                "marks_possible": module_ids_with_details[module][
                    "total_marks_possible"
                ],
                "taken_by_student": False,
                "total_assessment_credits": module_ids_with_details[module][
                    "total_assessment_credits"
                ],
                "total_module_credits": module_ids_with_details[module][
                    "total_module_credits"
                ],
            }
    # - COHORT
    # TODO: module_stats_cohort
    module_stats_cohort = {}

    # STORING OUTPUT AS .TXT FILES FOR EASE OF MY OWN USE
    # (if I was better I would only have this running in dev, not prod, but I'm not)
    # Write dictionary to CSV

    try:
        with open(
            "aat/student_stats/data_dumps/overall_results_cohort.txt", "w"
        ) as convert_file:
            convert_file.write(json.dumps(overall_results_cohort))
        with open(
            "aat/student_stats/data_dumps/overall_results_student.txt", "w"
        ) as convert_file:
            convert_file.write(json.dumps(overall_results_student))
        with open(
            "aat/student_stats/data_dumps/module_stats_student.txt", "w"
        ) as convert_file:
            convert_file.write(json.dumps(module_stats_student))
        with open(
            "aat/student_stats/data_dumps/module_stats_cohort.txt", "w"
        ) as convert_file:
            convert_file.write(json.dumps(module_stats_cohort))
    except:
        ...

    # RETURN

    return render_template(
        "1_student_stats_course_view.html",
        overall_results_cohort=overall_results_cohort,
        overall_results_student=overall_results_student,
        module_stats_student=module_stats_student,
        module_stats_cohort=module_stats_cohort,
    )


@student_stats.route("/module/")
@student_stats.route("/module/<int:module_id>")
def module_view(module_id=0):
    # Checks if logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    # Module Error Handling
    if Module.query.filter_by(module_id=module_id).first() is None:
        return redirect(url_for("student_stats.module_not_found", module_id=module_id))

    # db_utils calls
    all_assessment_marks_student = get_all_assessment_marks(
        input_user_id=current_user.id,
        highest_scoring_attempt_only=True,
        input_module_id=module_id,
        store_output_to_file=True,
    )
    all_response_details = get_all_response_details(
        input_user_id=current_user.id,
        highest_scoring_attempt_only=True,
        input_module_id=module_id,
        store_output_to_file=True,
    )

    # Takes details, unpacks based on module_id
    module_details = get_module_ids_with_details(input_module_id=module_id)[module_id]

    # MODULE DETAILS:
    module_details["sum_of_possible_marks_summative"] = 0
    module_details["sum_of_correct_marks_summative"] = 0
    module_details["sum_of_num_of_credits_summative"] = 0
    module_details["sum_of_possible_marks_formative"] = 0
    module_details["sum_of_correct_marks_formative"] = 0
    module_details["sum_of_num_of_credits_formative"] = 0

    # Adds values for Formative and Summative (combined to be calculated)
    for entry in all_assessment_marks_student:
        if entry["is_summative"]:
            module_details["sum_of_possible_marks_summative"] += entry["possible_marks"]
            module_details["sum_of_correct_marks_summative"] += entry["correct_marks"]
            module_details["sum_of_num_of_credits_summative"] += entry["num_of_credits"]
        else:
            module_details["sum_of_possible_marks_formative"] += entry["possible_marks"]
            module_details["sum_of_correct_marks_formative"] += entry["correct_marks"]
            module_details["sum_of_num_of_credits_formative"] += entry["num_of_credits"]

    # OVERALL RESULTS
    # Module total marks
    # - STUDENT
    overall_results_student = marks_dictionary.copy()
    for assessment_mark in all_assessment_marks_student:
        overall_results_student["sum_of_marks_awarded"] += assessment_mark[
            "correct_marks"
        ]
        overall_results_student["sum_of_marks_possible"] += assessment_mark[
            "possible_marks"
        ]

    list_of_assessments_completed_by_student = [
        item["assessment_id"] for item in all_assessment_marks_student
    ]

    # All assessments associated with module:
    q = Module.query.filter_by(module_id=module_id).all()
    assessments_not_taken_yet = []
    for m in q:
        for a in m.assessments:
            if a.assessment_id not in list_of_assessments_completed_by_student:
                assessments_not_taken_yet.append(a)

    print(assessments_not_taken_yet)

    return render_template(
        "2_student_stats_module_view.html",
        module_details=module_details,
        all_assessment_marks_student=all_assessment_marks_student,
        assessments_not_taken_yet=assessments_not_taken_yet,
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

    # TODO: validation for if no attempts (in routes)

    assessment_object = Assessment.query.filter_by(assessment_id=assessment_id).first()

    assessment_details = {
        "module_id": assessment_object.module_id,
        "module_title": assessment_object.module.title,
        "assessment_id": assessment_id,
        "assessment_title": assessment_object.title,
    }

    # db_utils calls
    all_assessment_marks_student = get_all_assessment_marks(
        input_user_id=current_user.id,
        highest_scoring_attempt_only=False,
        input_module_id=assessment_details["module_id"],
        input_assessment_id=assessment_id,
        store_output_to_file=True,
    )

    all_response_details = get_all_response_details(
        input_user_id=current_user.id,
        highest_scoring_attempt_only=False,
        input_module_id=assessment_details["module_id"],
        input_assessment_id=assessment_id,
        store_output_to_file=True,
    )

    ## Need to make dictionary of: {attempt_number : [all questions associated]}
    all_response_details_grouped_by_attempt_number = {}
    for r in all_response_details:
        if not r["attempt_number"] in all_response_details_grouped_by_attempt_number:
            all_response_details_grouped_by_attempt_number[r["attempt_number"]] = []
        all_response_details_grouped_by_attempt_number[r["attempt_number"]].append(r)

    total_score_per_attempt = (
        {}
    )  # dictionary of {attempt_id{correct_marks, possible_marks}}
    for attempt_id, responses in all_response_details_grouped_by_attempt_number.items():
        total_score_per_attempt[attempt_id] = {"correct_marks": 0, "possible_marks": 0}
        for r in responses:
            total_score_per_attempt[attempt_id]["correct_marks"] += (
                r["num_of_marks"] if r["is_correct"] else 0
            )
            total_score_per_attempt[attempt_id]["possible_marks"] += r["num_of_marks"]
        total_score_per_attempt[attempt_id][
            "mark_as_percentage"
        ] = f"{total_score_per_attempt[attempt_id]['correct_marks']/ total_score_per_attempt[attempt_id]['possible_marks']:.0%}"

    highest_scoring_response_details = get_all_response_details(
        input_user_id=current_user.id,
        highest_scoring_attempt_only=True,
        input_module_id=assessment_details["module_id"],
        input_assessment_id=assessment_id,
        store_output_to_file=True,
    )

    # Add marks from highest scoring attempt:
    ## loop over highest_scoring_response_details and get the marks
    assessment_details["sum_of_marks_awarded"] = 0
    assessment_details["sum_of_marks_possible"] = 0
    assessment_details["highest_scoring_attempt_number"] = 0

    for response in highest_scoring_response_details:
        assessment_details["sum_of_marks_possible"] += response["num_of_marks"]
        assessment_details["sum_of_marks_awarded"] += (
            response["num_of_marks"] if response["is_correct"] else 0
        )
        if assessment_details["highest_scoring_attempt_number"] == 0:
            assessment_details["highest_scoring_attempt_number"] = response[
                "attempt_number"
            ]

    # Variables required:
    # - labels: list of strings
    # - data: list of integers
    # - backgroundColor: list of rgba (strings)
    # - options (y axis should be total possible marks)

    data_for_bar_chart = {
        "labels": [],  # Attempt names
        "data": [],  # Attempt total marks achieved
        "backgroundColor": [],  # Red if below 50%, Blue if above
        "y_axis_max": 0,  # Highest marks
    }

    # Sort all_response_details_grouped_by_attempt_number
    for i in range(len(total_score_per_attempt)):
        response = total_score_per_attempt[i + 1]
        data_for_bar_chart["labels"].append(i + 1)
        data_for_bar_chart["data"].append(response["correct_marks"])
        data_for_bar_chart["backgroundColor"].append("54, 162, 235, 0.8") if (
            response["correct_marks"] / response["possible_marks"]
        ) > 0.5 else data_for_bar_chart["backgroundColor"].append("255, 99, 132, 0.8")
        data_for_bar_chart["y_axis_max"] = response["possible_marks"]

    return render_template(
        "3_student_stats_assessment_view.html",
        assessment_details=assessment_details,
        all_assessment_marks_student=all_assessment_marks_student,
        all_response_details=all_response_details,
        highest_scoring_response_details=highest_scoring_response_details,
        all_response_details_grouped_by_attempt_number=all_response_details_grouped_by_attempt_number,
        total_score_per_attempt=total_score_per_attempt,
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


@student_stats.route("/assessment/not-found/<int:assessment_id>")
def empty_assessment(assessment_id):
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
