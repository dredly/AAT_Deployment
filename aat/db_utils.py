# from . import db, app
from .models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions
import json


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


def get_module_ids_with_details(input_module_id=None, store_output_to_file=False):
    """
    Returns dictionary:
        [module_id (int): {
            module_title (string),
            total_module_credits (int),
            total_assessment_credits (int),
            total_marks_possible (int),
            module (Module),
            count_of_assessments (int)
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
    - difficulty (int)

    Optional filters added for student, lecturer, module and assessment id
    """

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
            QuestionT1.difficulty,  # 21
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
        output_dict["difficulty"] = question[21]

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
            QuestionT2.difficulty,  # 21
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
        output_dict["difficulty"] = question[21]

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

    return final_output
