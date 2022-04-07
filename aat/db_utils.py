# from . import db, app
from .models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions
import json
from collections import Counter

"""
To use db_utils from inside a blueprint:

- Import statement:
from ..db_utils import results_list_totals

- Call functions:
dictionary_of_results = results_list_totals()
"""

# STORING OUTPUT AS .TXT FILES FOR EASE OF MY OWN USE
# (if I was better I would only have this running in dev, not prod, but I'm not)
# Write dictionary to CSV
# FYI rename this file as .py and the VS code formatter makes it PRETTY
def store_dictionary_as_file(dictionary, filename):
    try:
        with open(
            f"{filename}",
            "w",
        ) as convert_file:
            convert_file.write(json.dumps(dictionary))
    except:
        ...


def get_assessment_id_and_total_marks_possible(store_output_to_file=False):
    """
    Returns dictionary: {assessment_id: total_possible_marks}
    (useful for combining question type 1 and type 2)
    """
    a = Assessment.query.all()
    assessment_id_and_total_marks_possible = {}
    for q in a:
        total_marks_possible = 0
        for q1 in q.question_t1:
            total_marks_possible += q1.num_of_marks
        for q2 in q.question_t2:
            total_marks_possible += q2.num_of_marks
        assessment_id_and_total_marks_possible[q.assessment_id] = total_marks_possible
    if store_output_to_file:
        store_dictionary_as_file(
            assessment_id_and_total_marks_possible,
            "aat/student_stats/data_dumps/assessment_id_and_total_marks_possible.txt",
        )

    return assessment_id_and_total_marks_possible


def get_assessment_id_and_data(store_output_to_file=False, module_id=None):
    """
    Returns dictionary: {assessment_id: total_possible_marks}
    (useful for combining question type 1 and type 2)
    """
    if module_id is not None:
        a = Assessment.query.filter_by(module_id=module_id).all()
    else:
        a = Assessment.query.all()
    assessment_id_and_data = {}
    for q in a:
        assessment_id_and_data[q.assessment_id] = {
            "total_marks_possible": 0,
            "count_of_questions": 0,
            "difficulty_array": [],
            "tag_array": [],
            "tag_name": [],
        }
        for q1 in q.question_t1:
            aid = assessment_id_and_data[q.assessment_id]
            aid["total_marks_possible"] += q1.num_of_marks
            aid["count_of_questions"] += 1
            aid["difficulty_array"].append(q1.difficulty)
            aid["tag_array"].append(q1.tag.name)

        for q2 in q.question_t2:
            aid = assessment_id_and_data[q.assessment_id]
            aid["total_marks_possible"] += q2.num_of_marks
            aid["count_of_questions"] += 1
            aid["difficulty_array"].append(q2.difficulty)
            aid["tag_array"].append(q2.tag.name)

    for a in assessment_id_and_data:
        aid = assessment_id_and_data[a]
        if not aid["count_of_questions"]:
            continue
        aid["average_difficulty"] = round(
            sum(aid["difficulty_array"]) / len(aid["difficulty_array"]), 1
        )
        aid["tag_array_counter"] = dict(Counter(aid["tag_array"]))

    if store_output_to_file:
        store_dictionary_as_file(
            assessment_id_and_data,
            "aat/student_stats/data_dumps/assessment_id_and_data.txt",
        )

    return assessment_id_and_data


def get_module_ids_with_details(input_module_id=None, store_output_to_file=False):
    """
    Returns dictionary:
        [module_id (int): {
            module_title (string),
            total_module_credits (int),
            total_assessment_credits (int),
            total_marks_possible (int),
            module (Module),
            count_of_assessments, (int)
            count_of_formative_assessments, (int)
            count_of_summative_assessments, (int)
            }]
    """
    q = (
        Module.query.all()
        if not input_module_id
        else Module.query.filter(Module.module_id == input_module_id).all()
    )

    output_dict = {}

    for module in q:
        output_dict[module.module_id] = {
            "module_title": module.title,
            "total_assessment_credits": 0,
            "total_marks_possible": 0,
            "count_of_assessments": len(module.assessments),
            "count_of_formative_assessments": len(
                [m for m in module.assessments if not m.is_summative]
            ),
            "count_of_summative_assessments": len(
                [m for m in module.assessments if m.is_summative]
            ),
        }
        # Find all assessments connected
        for assessment in module.assessments:
            output_dict[module.module_id][
                "total_assessment_credits"
            ] += assessment.num_of_credits

            # Q1
            for q1 in assessment.question_t1:
                output_dict[module.module_id]["total_marks_possible"] += q1.num_of_marks
            # Q2
            for q2 in assessment.question_t2:
                output_dict[module.module_id]["total_marks_possible"] += q2.num_of_marks

    for module in q:
        output_dict[module.module_id]["total_module_credits"] = output_dict[
            module.module_id
        ]["total_assessment_credits"]

    if store_output_to_file:
        store_dictionary_as_file(
            output_dict,
            "aat/student_stats/data_dumps/module_ids_with_details.txt",
        )

    # Will then need to go through the question types
    return output_dict


def set_highest_scoring_attempt(dictionary_of_responses):
    # Add a "highest_scoring_attempt" attribute for if this attempt is the HIGHEST scoring attempt the user has made
    for row in dictionary_of_responses:
        row["highest_scoring_attempt"] = True
        for comparison in dictionary_of_responses:
            if (
                row is not comparison
                and row["user_id"] == comparison["user_id"]
                and row["module_id"] == comparison["module_id"]
                and row["assessment_id"] == comparison["assessment_id"]
            ):
                if comparison["correct_marks"] > row["correct_marks"]:
                    row["highest_scoring_attempt"] = False
    return dictionary_of_responses


def get_all_assessment_marks(
    input_user_id=None,
    input_lecturer_id=None,
    input_module_id=None,
    input_assessment_id=None,
    highest_scoring_attempt_only=False,
    summative_only=False,
    debug=False,
    store_output_to_file=False,
):
    """
    Returns list of dictionaries, each dictionary has the following keys:
    - 'user_id' (int)
    - 'module_id' (int)
    - 'assessment_id' (int)
    - 'lecturer_id' (int)
    - 'attempt_number' (int)
    - 'correct_marks' (int)
    - 'possible_marks' (int)
    - 'highest_scoring_attempt' (bool)
    - 'num_of_credits' (int)
    - 'is_summative' (bool)
    - 'module_title' (str)
    - 'assessment_title' (str)
    - 'passed' (bool)
    - 'credits_earned' (int)
    - 'difficulty_average' (int)
    ' 'list_of_tags' ([str])

    Optional filters added for student, lecturer, module and assessment id
    print statements are enabled/disabled through debug=True/False
    """
    attempt_totals_t1 = (
        db.session.query(User, QuestionT1, ResponseT1, Module, Assessment)
        .with_entities(
            User.id,  # 0
            Module.module_id,  # 1
            Assessment.assessment_id,  # 2
            Assessment.lecturer_id,  # 3
            ResponseT1.attempt_number,  # 4
            func.sum(QuestionT1.num_of_marks)  # 5
            .filter(ResponseT1.is_correct == True)
            .label("correct_marks"),
            Assessment.num_of_credits,  # 6
            Assessment.is_summative,  # 7
            Module.title,  # 8
            Assessment.title,  # 9
        )
        .select_from(User)
        .join(ResponseT1)
        .join(QuestionT1)
        .join(Assessment)
        .join(Module)
        .group_by(User.id)
        .group_by(Module.module_id)
        .group_by(Assessment.assessment_id)
        .group_by(Assessment.lecturer_id)
        .group_by(ResponseT1.attempt_number)
    )

    if debug:
        print("***")
        print("Attempts Total T1")
        for items in attempt_totals_t1:
            pprint(f"{items}")

    attempt_totals_t2 = (
        db.session.query(User, QuestionT2, ResponseT2, Module, Assessment)
        .with_entities(
            User.id,
            Module.module_id,
            Assessment.assessment_id,
            Assessment.lecturer_id,
            ResponseT2.attempt_number,
            func.sum(QuestionT2.num_of_marks)
            .filter(ResponseT2.is_correct == True)
            .label("correct_marks"),
            Assessment.num_of_credits,
            Assessment.is_summative,
            Module.title,
            Assessment.title,
        )
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .join(Module)
        .group_by(User.id)
        .group_by(Module.module_id)
        .group_by(Assessment.assessment_id)
        .group_by(Assessment.lecturer_id)
        .group_by(ResponseT2.attempt_number)
    )

    if debug:
        print("***")
        print("Attempts Total T2")
        for items in attempt_totals_t2:
            pprint(f"{items}")

    # UNION: https://docs.sqlalchemy.org/en/14/orm/query.html
    all_values = attempt_totals_t1.union_all(attempt_totals_t2)

    if debug:
        print("***")
        print("All values:")
        for items in all_values:
            pprint(f"{items}")

    assessment_id_and_total_marks_possible = (
        get_assessment_id_and_total_marks_possible()
    )

    if debug:
        print("****")
        print(f"{assessment_id_and_total_marks_possible=}")
        print("****")

    final_output = []

    # Make list of dictionaries holding relevant IDs and summations of correct marks
    for row in all_values:
        add_to_dict = True
        marks_dict = {}
        user_id = row[0]
        module_id = row[1]
        assessment_id = row[2]
        lecturer_id = row[3]
        attempt_number = row[4]
        correct_marks = row[5] if row[5] is not None else 0
        possible_marks = assessment_id_and_total_marks_possible[assessment_id]
        num_of_credits = row[6]
        is_summative = row[7]
        module_title = row[8]
        assessment_title = row[9]
        # Is it already in the final_output? If so, adjust that
        for entry in final_output:
            if (
                entry["user_id"] == user_id
                and entry["module_id"] == module_id
                and entry["assessment_id"] == assessment_id
                and entry["attempt_number"] == attempt_number
            ):
                entry["correct_marks"] += correct_marks
                add_to_dict = False

        # If no adjustment happened then append to final_output
        if add_to_dict:
            marks_dict["user_id"] = user_id
            marks_dict["module_id"] = module_id
            marks_dict["assessment_id"] = assessment_id
            marks_dict["lecturer_id"] = lecturer_id
            marks_dict["attempt_number"] = attempt_number
            marks_dict["correct_marks"] = correct_marks
            marks_dict["possible_marks"] = possible_marks
            marks_dict["num_of_credits"] = num_of_credits
            marks_dict["is_summative"] = is_summative
            marks_dict["module_title"] = module_title
            marks_dict["assessment_title"] = assessment_title

            final_output.append(marks_dict)

    if debug:
        print("***")
        pprint(f"final_output_before_highest_flag=")
        pprint(final_output)

    final_output = set_highest_scoring_attempt(final_output)

    # Add a "highest_scoring_attempt" attribute for if this attempt is the HIGHEST scoring attempt the user has made
    for row in final_output:
        row["highest_scoring_attempt"] = True
        for comparison in final_output:
            if (
                row is not comparison
                and row["user_id"] == comparison["user_id"]
                and row["module_id"] == comparison["module_id"]
                and row["assessment_id"] == comparison["assessment_id"]
            ):
                if comparison["correct_marks"] > row["correct_marks"]:
                    row["highest_scoring_attempt"] = False

    # PASSED
    for row in final_output:
        percentage_achieved = row["correct_marks"] / row["possible_marks"]
        row["passed"] = True if percentage_achieved >= 0.5 else False
        row["credits_earned"] = (
            row["num_of_credits"]
            if row["passed"] and row["highest_scoring_attempt"]
            else 0
        )

    ###########
    # FILTERS #
    ###########

    # User_ID
    if input_user_id:
        final_output = [
            item for item in final_output if item["user_id"] == input_user_id
        ]
    # Lecturer_ID
    if input_lecturer_id:
        final_output = [
            item for item in final_output if item["lecturer_id"] == input_lecturer_id
        ]
    # Module_ID
    if input_module_id:
        final_output = [
            item for item in final_output if item["module_id"] == input_module_id
        ]
    # Assessment_ID
    if input_assessment_id:
        final_output = [
            item
            for item in final_output
            if item["assessment_id"] == input_assessment_id
        ]
    # Highest Scoring Attempt Only
    if highest_scoring_attempt_only:
        final_output = [
            item for item in final_output if item["highest_scoring_attempt"]
        ]
    # Summative Only
    if summative_only:
        final_output = [item for item in final_output if item["is_summative"]]

    if store_output_to_file:
        store_dictionary_as_file(
            final_output,
            "aat/student_stats/data_dumps/all_assessment_marks.txt",
        )

    return final_output


########################################################################


def get_all_response_details(
    input_user_id=None,
    input_lecturer_id=None,
    input_module_id=None,
    input_assessment_id=None,
    highest_scoring_attempt_only=False,
    store_output_to_file=False,
):
    """
    Returns a list of dictionaries gathering all relevant response details:
    - user_id (int)
    - attempt_number (int)
    - question_id (int)
    - question_text (str)
    - question_difficulty (int)
    - answer_given (str)
    - is_correct (bool)
    - lecturer_id (int)
    - num_of_marks (int)
    - module_id (int)
    - assessment_id (int)
    - question_type (int, 1 or 2)
    - correct_answer (str)
    - feedback (str)
    - feedforward (str)
    - highest_scoring_attempt (bool)
    - student_email (str)
    - lecturer_email (str)
    - tag_id (int)
    - tag_name (str)

    Optional filters added for student, lecturer, module and assessment id
    """
    q1_q = ResponseT1.query.all()
    print(f"{q1_q=}")
    # TYPE 1
    question_totals_t1 = (
        db.session.query(User, QuestionT1, ResponseT1, Option, Module, Assessment)
        .with_entities(
            User.id,  # 0
            ResponseT1.attempt_number,  # 1
            QuestionT1.q_t1_id,  # 2
            QuestionT1.question_text,  # 3
            QuestionT1.difficulty,  # 4
            Option.option_text,  # 5
            ResponseT1.is_correct,  # 6
            Assessment.lecturer_id,  # 7
            QuestionT1.num_of_marks,  # 8
            Module.module_id,  # 9
            Assessment.assessment_id,  # 10
            QuestionT1.feedback_if_correct,  # 11
            QuestionT1.feedback_if_wrong,  # 12
            QuestionT1.feedforward_if_correct,  # 13
            QuestionT1.feedback_if_wrong,  # 14
            ResponseT1,  # 15
            Assessment.is_summative,  # 16
            Assessment.num_of_credits,  # 17
            Module.title,  # 18
            Assessment.title,  # 19
            QuestionT1.tag_id,  # 20
        )
        .select_from(User)
        .join(ResponseT1)
        .join(Option)
        .join(QuestionT1)
        .join(Assessment)
        .join(Module)
        .group_by(User.id)
        .group_by(ResponseT1.attempt_number)
        .group_by(QuestionT1.q_t1_id)
        .group_by(Assessment.lecturer_id)
        .group_by(Module.module_id)
        .group_by(Assessment.assessment_id)
    )

    # print(f"RAW T1: {question_totals_t1.all()=}")

    table_of_correct_t1_answers = Option.query.filter(Option.is_correct == True)

    # Should be able to do this as a join but not working so I'm going the LONG way round to sort
    t1_output = []
    for question in question_totals_t1:
        output_dict = {}
        output_dict["user_id"] = question[0]
        output_dict["attempt_number"] = question[1]
        output_dict["question_id"] = question[2]
        output_dict["question_text"] = question[3]
        output_dict["question_difficulty"] = question[4]
        output_dict["answer_given"] = question[5]
        output_dict["is_correct"] = question[6]
        output_dict["lecturer_id"] = question[7]
        output_dict["num_of_marks"] = question[8]
        output_dict["module_id"] = question[9]
        output_dict["assessment_id"] = question[10]
        output_dict["question_type"] = 1
        output_dict["is_summative"] = question[16]
        output_dict["num_of_credits"] = question[17]
        output_dict["module_title"] = question[18]
        output_dict["assessment_title"] = question[19]
        output_dict["tag_id"] = question[20]

        for answer in table_of_correct_t1_answers:
            if answer.q_t1_id == output_dict["question_id"]:
                output_dict["correct_answer"] = answer.option_text

        ## ADD FEEDBACK/FEEDFORWARD IF CORRECT/INCORRECT
        output_dict["feedback"] = (
            question[11] if output_dict["is_correct"] else question[12]
        )
        output_dict["feedforward"] = (
            question[13] if output_dict["is_correct"] else question[14]
        )

        t1_output.append(output_dict)

    # TYPE 2
    question_totals_t2 = (
        db.session.query(User, QuestionT2, ResponseT2, Option, Module, Assessment)
        .with_entities(
            User.id,  # 0
            ResponseT2.attempt_number,  # 1
            QuestionT2.q_t2_id,  # 2
            QuestionT2.question_text,  # 3
            QuestionT2.difficulty,  # 4
            ResponseT2.response_content,  # 5
            ResponseT2.is_correct,  # 6
            Assessment.lecturer_id,  # 7
            QuestionT2.num_of_marks,  # 8
            Module.module_id,  # 9
            Assessment.assessment_id,  # 10
            QuestionT2.correct_answer,  # 11
            QuestionT2.feedback_if_correct,  # 12
            QuestionT2.feedback_if_wrong,  # 13
            QuestionT2.feedforward_if_correct,  # 14
            QuestionT2.feedforward_if_wrong,  # 15
            Assessment.is_summative,  # 16
            Assessment.num_of_credits,  # 17
            Module.title,  # 18
            Assessment.title,  # 19
            QuestionT2.tag_id,
        )
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .join(Module)
        .group_by(User.id)
        .group_by(ResponseT2.attempt_number)
        .group_by(QuestionT2.q_t2_id)
        .group_by(Assessment.lecturer_id)
        .group_by(Module.module_id)
        .group_by(Assessment.assessment_id)
    )

    # Should be able to do this as a join but not working
    t2_output = []

    for question in question_totals_t2:
        output_dict = {}
        output_dict["user_id"] = question[0]
        output_dict["attempt_number"] = question[1]
        output_dict["question_id"] = question[2]
        output_dict["question_text"] = question[3]
        output_dict["question_difficulty"] = question[4]
        output_dict["answer_given"] = question[5]
        output_dict["is_correct"] = question[6]
        output_dict["lecturer_id"] = question[7]
        output_dict["num_of_marks"] = question[8]
        output_dict["module_id"] = question[9]
        output_dict["assessment_id"] = question[10]
        output_dict["question_type"] = 2
        output_dict["correct_answer"] = question[11]
        output_dict["is_summative"] = question[16]
        output_dict["num_of_credits"] = question[17]
        output_dict["module_title"] = question[18]
        output_dict["assessment_title"] = question[19]
        output_dict["tag_id"] = question[20]

        ## ADD FEEDBACK/FEEDFORWARD IF CORRECT/INCORRECT
        output_dict["feedback"] = (
            question[12] if output_dict["is_correct"] else question[13]
        )
        output_dict["feedforward"] = (
            question[14] if output_dict["is_correct"] else question[15]
        )
        t2_output.append(output_dict)

    final_output = t1_output + t2_output

    #####################
    # ADDITIONAL FIELDS #
    #####################
    for item in final_output:
        # Add tag names
        item["tag_name"] = (
            Tag.query.with_entities(Tag.name).filter_by(id=item["tag_id"]).first()
        )

        # Add student email addresses
        item["student_email"] = (
            User.query.with_entities(User.email)
            .filter_by(id=item["user_id"])
            .first()[0]
        )

        # Add lecturer email addresses
        item["lecturer_email"] = (
            User.query.with_entities(User.email)
            .filter_by(id=item["lecturer_id"])
            .first()[0]
        )

    all_assessment_marks = get_all_assessment_marks()

    # Add a field saying if that response is part of the highest scoring attempt
    for item in final_output:
        for assessment_details in all_assessment_marks:
            if (
                item["user_id"] == assessment_details["user_id"]
                and item["module_id"] == assessment_details["module_id"]
                and item["assessment_id"] == assessment_details["assessment_id"]
                and item["attempt_number"] == assessment_details["attempt_number"]
            ):
                item["highest_scoring_attempt"] = assessment_details[
                    "highest_scoring_attempt"
                ]

    # print(f"Output BEFORE filters: {final_output=}")

    # FILTERS
    if input_user_id:
        final_output = [
            item for item in final_output if item["user_id"] == input_user_id
        ]
    if input_lecturer_id:
        final_output = [
            item for item in final_output if item["lecturer_id"] == input_lecturer_id
        ]
    if input_module_id:
        final_output = [
            item for item in final_output if item["module_id"] == input_module_id
        ]
    if input_assessment_id:
        final_output = [
            item
            for item in final_output
            if item["assessment_id"] == input_assessment_id
        ]
    if highest_scoring_attempt_only:
        final_output = [
            item for item in final_output if item["highest_scoring_attempt"]
        ]

    if store_output_to_file:
        store_dictionary_as_file(
            final_output,
            "aat/student_stats/data_dumps/all_response_details.txt",
        )

    # print(f"Output AFTER filters: {final_output=}")

    return final_output


######################
# STATUS CALCULATORS #
######################
"""
Only summative assessments are considered for the below (i.e. formative assessments do not contribute)

An assessment's credit_weighting = credits_possible / total_credits_possible_for_the_module

Overall weighted_percentage = (marks_earned/total_marks_for_assessment) * credit_weighting

A module is passed if its assessment's total_weighted_percentages >= 50%

You then earn all credits for that module

A course is passed if all modules are passed (i.e. total_earned_credits==total_possible_credits)

STATUS:
- ASSESSMENT:
-- pass: total_marks >= 50%
-- fail: total_marks < 50%
-- unattempted: student hasn't taken it

- MODULE:
-- pass: total_weighted_percentage >= 50%
-- fail: total_weighted_percentage < 50% AND all assessments attempted
-- in progress: total_weighted_percentage < 50% AND all assessments NOT attempted
-- unattempted: no assessments have been attempted

- COURSE:
-- pass: all modules have "pass" status
-- fail: all modules have "fail" status
-- in progress: any modules have "in progress" status
-- unattempted: all modules have "unattempted" status
"""

# UTIL
def get_total_credits_for_module(module_id):
    assessment_query = (
        Assessment.query.filter_by(module_id=module_id)
        .filter_by(is_summative=True)
        .all()
    )
    total_credits_for_module = sum([a.num_of_credits for a in assessment_query])
    return total_credits_for_module


def get_total_marks_for_assessment(assessment_id):
    assessment_query = (
        Assessment.query.filter_by(assessment_id=assessment_id)
        .filter_by(is_summative=True)
        .all()
    )
    total_marks_for_assessment = 0
    for q in assessment_query:
        for q1 in q.question_t1:
            total_marks_for_assessment += q1.num_of_marks
    for q in assessment_query:
        for q2 in q.question_t2:
            total_marks_for_assessment += q2.num_of_marks

    return total_marks_for_assessment


def get_weighted_perc_calc(marks_earned, assessment_id):
    """
    Takes in the marks earned and the assessment ID
    Returns the weighted mark based on the total credits possible in that module
    """
    assessment_query = Assessment.query.filter_by(assessment_id=assessment_id).first()

    module_id = assessment_query.module_id
    credits_for_assessment = assessment_query.num_of_credits

    total_credits_for_module = get_total_credits_for_module(module_id)
    total_marks_for_assessment = get_total_marks_for_assessment(assessment_id)

    weighted_mark = (marks_earned / total_marks_for_assessment) * (
        credits_for_assessment / total_credits_for_module
    )

    return weighted_mark


# MAIN
def get_assessment_status(assessment_id, user_id):
    """
    Takes in marks_earned, assessment_id and user_id and returns a status (string):
    - "pass"
    - "fail"
    - "unattempted"
    """
    assessment_query = Assessment.query.filter_by(assessment_id=assessment_id).first()
    # UNATTEMPTED
    if (
        ResponseT1.query.filter_by(assessment_id=assessment_id)
        .filter_by(user_id=user_id)
        .first()
        is None
        and ResponseT2.query.filter_by(assessment_id=assessment_id)
        .filter_by(user_id=user_id)
        .first()
        is None
    ):
        return "unattempted"

    # WHERE HAS MARKS EARNED GONE??
    assessment_marks = get_all_assessment_marks(
        input_user_id=user_id,
        input_module_id=module_id,
        input_assessment_id=assessment_id,
        highest_scoring_attempt_only=True,
        summative_only=True,
    )

    marks_earned = sum([q["correct_marks"] for q in all_assessment_marks])

    # PASS OR FAIL
    sum_of_all_marks_in_assessment = get_total_marks_for_assessment(assessment_id)
    if (marks_earned / sum_of_all_marks_in_assessment) >= 0.5:
        return "pass"
    else:
        return "fail"


def get_module_status(module_id, user_id):
    all_assessment_marks = get_all_assessment_marks(
        input_user_id=user_id,
        input_module_id=module_id,
        highest_scoring_attempt_only=True,
        summative_only=True,
    )

    # If there are no marks, an empty list is returned
    if not all_assessment_marks:
        return "unattempted"

    assessments_taken = {
        q["assessment_id"]: q["correct_marks"] for q in all_assessment_marks
    }

    total_weighted_perc = sum(
        [
            get_weighted_perc_calc(marks_earned, assessment_id)
            for assessment_id, marks_earned in assessments_taken.items()
        ]
    )

    # If they're above 50% at any point they've passed
    if total_weighted_perc >= 0.5:
        return "pass"

    a = (
        Assessment.query.filter_by(module_id=module_id)
        .filter_by(is_summative=True)
        .all()
    )

    list_of_all_assessment_ids = [a.assessment_id for a in a]

    # If they've tried all assessments but they're still below 50%
    if len(list_of_all_assessment_ids) == len(all_assessment_marks):
        return "fail"
    return "in progress"


def get_course_status(user_id):
    module_query = Module.query.all()
    number_of_modules = len(module_query)
    array_of_module_statuses = [
        get_module_status(m.module_id, user_id) for m in module_query
    ]

    count_of_status = dict(Counter(array_of_module_statuses))

    if count_of_status.get("pass") == number_of_modules:
        return "pass"
    elif count_of_status.get("fail") == number_of_modules:
        return "fail"
    elif count_of_status.get("in progress", 0) > 0:
        return "in progress"
    else:
        return "unattempted"
