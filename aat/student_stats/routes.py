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
    overall_results_student = {
        "sum_of_marks_awarded": 0,
        "sum_of_marks_possible": 0,
        "total_credits_possible": 0,
        "total_credits_earned": 0,
    }

    for assessment_mark in all_assessment_marks_student:
        overall_results_student["sum_of_marks_awarded"] += assessment_mark[
            "correct_marks"
        ]
        overall_results_student["sum_of_marks_possible"] += assessment_mark[
            "possible_marks"
        ]
        overall_results_student["total_credits_possible"] += assessment_mark[
            "num_of_credits"
        ]
        overall_results_student["total_credits_earned"] += assessment_mark[
            "credits_earned"
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

    # Dict of modules, how many assessments are in it, how many you've completed
    dict_of_assessment_counts = {}
    for module in module_ids_with_details:
        dict_of_assessment_counts[module] = {
            "count_of_assessments": module_ids_with_details[module][
                "count_of_assessments"
            ],
            "count_of_taken_assessments": 0,
        }
    for assessment_id in list_of_assessments_completed_by_student:
        a = Assessment.query.filter_by(assessment_id=assessment_id).first()
        dict_of_assessment_counts[a.module.module_id]["count_of_taken_assessments"] += 1

    # print(f"{all_assessment_marks_student=}")
    for m in dict_of_assessment_counts:
        for a in all_assessment_marks_student:
            if m == a["module_id"]:
                # print(a)
                dict_of_assessment_counts[m]["count_of_passed_assessments"] = (
                    dict_of_assessment_counts[m].get("count_of_passed_assessments", 0)
                    + 1
                )

    module_ids = module_ids_with_details.keys()

    dictionary_of_module_credits = {}
    for id in module_ids:
        dictionary_of_module_credits[id] = {
            "total_credits_possible": 0,
            "total_credits_earned": 0,
        }

    for module_id in module_ids:
        for assessment in all_assessment_marks_student:
            if assessment["module_id"] == module_id:
                dictionary_of_module_credits[module_id][
                    "total_credits_earned"
                ] += assessment["credits_earned"]

    total_credits_possible = 0
    query_of_assessments = Assessment.query.all()
    for q in query_of_assessments:
        dictionary_of_module_credits[q.module_id][
            "total_credits_possible"
        ] += q.num_of_credits
        total_credits_possible += q.num_of_credits

    total_credits_earned = sum(
        [a["credits_earned"] for a in all_assessment_marks_student]
    )
    dictionary_of_module_credits["total"] = {
        "total_credits_possible": total_credits_possible,
        "total_credits_earned": total_credits_earned,
    }

    # dict_of_module_id_and_credits = []
    # for module_id in :
    #     total_credits_possible = 0
    #     total_credits_earned = 0
    #     for a in all_assessment_marks_student:
    #         print("!!!!")
    #         print(a)
    #         print(all_assessment_marks_student)
    #         if a["user_id"] == module_id:
    #             total_credits_possible += a["num_of_credits"]
    #             total_credits_earned += a["credits_earned"]
    #     dict_of_module_id_and_credits.append(
    #         {
    #             "module_id": a["user_id"],
    #             "total_credits_possible": total_credits_possible,
    #             "total_credits_earned": total_credits_earned,
    #         }
    #     )

    # MODULE RESULTS
    # - STUDENT
    module_stats_student = {}
    for assessment_mark in all_assessment_marks_student:
        k = assessment_mark["module_id"]
        module_stats_student[k] = {
            "marks_awarded": assessment_mark["correct_marks"],
            "marks_possible": assessment_mark["possible_marks"],
            "taken_by_student": True,
        }

    # - > ADD MODULE STATS
    for module in module_ids_with_details:
        # Add stats for taken:

        if module in module_stats_student:
            module_stats_student[module]["module_title"] = module_ids_with_details[
                module
            ]["module_title"]
            module_stats_student[module][
                "total_assessment_credits"
            ] = module_ids_with_details[module]["total_assessment_credits"]
            module_stats_student[module][
                "count_of_assessments"
            ] = dict_of_assessment_counts[module]["count_of_assessments"]
            module_stats_student[module][
                "count_of_taken_assessments"
            ] = dict_of_assessment_counts[module]["count_of_taken_assessments"]
            module_stats_student[module][
                "count_of_passed_assessments"
            ] = dict_of_assessment_counts[module]["count_of_passed_assessments"]

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
                "count_of_assessments": dict_of_assessment_counts[module][
                    "count_of_assessments"
                ],
            }

    for id in module_ids_with_details.keys():
        entry = module_ids_with_details[id]
        # Isn't this what I need?

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

    # TAG

    # Get all responses
    all_response_details_for_tags = get_all_response_details(
        input_user_id=current_user.id
    )

    list_of_tags = Tag.query.all()

    dict_of_tags = {}
    for tag in list_of_tags:
        dict_of_tags[tag.name] = {"correct": 0, "incorrect": 0}

    dict_of_tags["untagged"] = {"correct": 0, "incorrect": 0}

    for response in all_response_details_for_tags:
        if response["tag_name"] is None:
            if response["is_correct"]:
                dict_of_tags["untagged"]["correct"] += 1
            else:
                dict_of_tags["untagged"]["incorrect"] += 1
        else:
            if response["is_correct"]:
                dict_of_tags[response["tag_name"][0]]["correct"] += 1
            else:
                dict_of_tags[response["tag_name"][0]]["incorrect"] += 1

    # Add perc and count_of_questions
    for tag in dict_of_tags:
        if dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"] > 0:
            dict_of_tags[tag]["perc"] = dict_of_tags[tag]["correct"] / (
                dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"]
            )
            dict_of_tags[tag]["count_of_questions"] = (
                dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"]
            )
        else:
            dict_of_tags[tag]["perc"] = None

    # Add strongest and weakest flags
    strongest_val = 0  # to be HIGHEST
    weakest_val = 1  # to be LOWEST

    for tag in dict_of_tags:
        if dict_of_tags[tag]["perc"] != None:
            if dict_of_tags[tag]["perc"] > strongest_val:
                strongest_val = dict_of_tags[tag]["perc"]
            if dict_of_tags[tag]["perc"] < weakest_val:
                weakest_val = dict_of_tags[tag]["perc"]

    # Gives all tags a status of strongest, weakest or ""
    for tag in dict_of_tags:
        if dict_of_tags[tag]["perc"] != None:
            if dict_of_tags[tag]["perc"] == strongest_val:
                dict_of_tags[tag]["status"] = "strongest"
            elif dict_of_tags[tag]["perc"] == weakest_val:
                dict_of_tags[tag]["status"] = "weakest"
            else:
                dict_of_tags[tag]["status"] = ""
        else:
            dict_of_tags[tag]["status"] = ""

    # MAKE TOTALS
    tag_totals = {"all_questions": 0, "all_correct": 0, "all_incorrect": 0}
    for tag in dict_of_tags:
        if dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"] > 0:
            tag_totals["all_questions"] += dict_of_tags[tag]["count_of_questions"]
            tag_totals["all_correct"] += dict_of_tags[tag]["correct"]
            tag_totals["all_incorrect"] += dict_of_tags[tag]["incorrect"]

    # print(module_stats_student)

    return render_template(
        "1_student_stats_course_view.html",
        overall_results_cohort=overall_results_cohort,
        overall_results_student=overall_results_student,
        module_stats_student=module_stats_student,
        module_stats_cohort=module_stats_cohort,
        dict_of_assessment_counts=dict_of_assessment_counts,
        dict_of_tags=dict_of_tags,
        tag_totals=tag_totals,
        dictionary_of_module_credits=dictionary_of_module_credits,
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

    assessment_object = Assessment.query.filter_by(assessment_id=assessment_id).first()

    assessment_details = {
        "module_id": assessment_object.module_id,
        "module_title": assessment_object.module.title,
        "assessment_id": assessment_id,
        "assessment_title": assessment_object.title,
        "summative_or_formative": "Summative"
        if assessment_object.is_summative
        else "Formative",
        "credits": assessment_object.num_of_credits,
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

    if (
        total_score_per_attempt[assessment_details["highest_scoring_attempt_number"]][
            "correct_marks"
        ]
        / total_score_per_attempt[assessment_details["highest_scoring_attempt_number"]][
            "possible_marks"
        ]
        >= 0.5
    ):
        assessment_details["highest_scoring_attempt_passed"] = True
    else:
        assessment_details["highest_scoring_attempt_passed"] = False

    ############
    # TAG DATA #
    ############

    # Can use "highest_scoring_response_details" as it will go over each question ONCE
    # TAG
    tag_dictionary = {}
    # Make all the empty dicts
    for r in highest_scoring_response_details:
        tag_dictionary[r["tag_name"][0]] = {
            "count": 0,
            "correct_in_highest": 0,
            "correct_in_all": 0,
        }

    for r in highest_scoring_response_details:
        tag_dictionary[r["tag_name"][0]]["count"] += 1
        if r["is_correct"]:
            tag_dictionary[r["tag_name"][0]]["correct_in_highest"] += 1

    ##############
    # CHART DATA #
    ##############

    data_for_bar_chart = {
        "labels": [],  # Attempt names
        "data": [],  # Attempt total marks achieved
        "backgroundColor": [],  # Red if below 50%, Blue if above
        "y_axis_max": 0,  # Highest marks
        "pass_mark": [],
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
        data_for_bar_chart["pass_mark"].append(response["possible_marks"] / 2)

    print(f"{assessment_details=}")

    return render_template(
        "3_student_stats_assessment_view.html",
        assessment_details=assessment_details,
        all_assessment_marks_student=all_assessment_marks_student,
        all_response_details=all_response_details,
        highest_scoring_response_details=highest_scoring_response_details,
        all_response_details_grouped_by_attempt_number=all_response_details_grouped_by_attempt_number,
        total_score_per_attempt=total_score_per_attempt,
        data_for_bar_chart=data_for_bar_chart,
        tag_dictionary=tag_dictionary,
    )


############
# TAG VIEW #
############


# @student_stats.route("/tag/")
# def tag_view():
#     # Checks if logged in
#     if not current_user.is_authenticated:
#         return redirect(url_for("auth.login"))

#     # Get all responses
#     all_response_details_for_tags = get_all_response_details(
#         input_user_id=current_user.id
#     )

#     list_of_tags = Tag.query.all()

#     dict_of_tags = {}
#     for tag in list_of_tags:
#         dict_of_tags[tag.name] = {"correct": 0, "incorrect": 0}

#     dict_of_tags["untagged"] = {"correct": 0, "incorrect": 0}

#     for response in all_response_details_for_tags:
#         if response["tag_name"] is None:
#             if response["is_correct"]:
#                 dict_of_tags["untagged"]["correct"] += 1
#             else:
#                 dict_of_tags["untagged"]["incorrect"] += 1
#         else:
#             if response["is_correct"]:
#                 dict_of_tags[response["tag_name"][0]]["correct"] += 1
#             else:
#                 dict_of_tags[response["tag_name"][0]]["incorrect"] += 1

#     # Add perc and count_of_questions
#     for tag in dict_of_tags:
#         if dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"] > 0:
#             dict_of_tags[tag]["perc"] = dict_of_tags[tag]["correct"] / (
#                 dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"]
#             )
#             dict_of_tags[tag]["count_of_questions"] = (
#                 dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"]
#             )
#         else:
#             dict_of_tags[tag]["perc"] = None

#     # Add strongest and weakest flags
#     strongest_val = 0  # to be HIGHEST
#     weakest_val = 1  # to be LOWEST

#     for tag in dict_of_tags:
#         if dict_of_tags[tag]["perc"] != None:
#             if dict_of_tags[tag]["perc"] > strongest_val:
#                 strongest_val = dict_of_tags[tag]["perc"]
#             if dict_of_tags[tag]["perc"] < weakest_val:
#                 weakest_val = dict_of_tags[tag]["perc"]

#     # Gives all tags a status of strongest, weakest or ""
#     for tag in dict_of_tags:
#         if dict_of_tags[tag]["perc"] != None:
#             if dict_of_tags[tag]["perc"] == strongest_val:
#                 dict_of_tags[tag]["status"] = "strongest"
#             elif dict_of_tags[tag]["perc"] == weakest_val:
#                 dict_of_tags[tag]["status"] = "weakest"
#             else:
#                 dict_of_tags[tag]["status"] = ""
#         else:
#             dict_of_tags[tag]["status"] = ""

#     # MAKE TOTALS
#     tag_totals = {"all_questions": 0, "all_correct": 0, "all_incorrect": 0}
#     for tag in dict_of_tags:
#         if dict_of_tags[tag]["correct"] + dict_of_tags[tag]["incorrect"] > 0:
#             tag_totals["all_questions"] += dict_of_tags[tag]["count_of_questions"]
#             tag_totals["all_correct"] += dict_of_tags[tag]["correct"]
#             tag_totals["all_incorrect"] += dict_of_tags[tag]["incorrect"]

#     return render_template(
#         "4_tag.html", dict_of_tags=dict_of_tags, tag_totals=tag_totals
#     )


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
