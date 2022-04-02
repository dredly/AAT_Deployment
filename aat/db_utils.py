# from . import db, app
from .models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions


"""
To use db_utils from inside a blueprint:

- Import statement:
from ..db_utils import results_list_totals

- Call functions:
dictionary_of_results = results_list_totals()
"""


def get_all_assessment_marks():
    """
    Returns list of dictionaries, each dictionary has the following keys:
    - 'user_id' (int)
    - 'module_id' (int)
    - 'assessment_id' (int)
    - 'lecturer_id' (int)
    - 'attempt_number' (int)
    - 'correct_marks' (int)
    - 'possible_marks' (int)
    - 'highest_value' (bool)
    """
    attempt_totals_t1 = (
        db.session.query(User, QuestionT1, ResponseT1, Module, Assessment)
        .with_entities(
            User.id,
            Module.module_id,
            Assessment.assessment_id,
            Assessment.lecturer_id,
            ResponseT1.attempt_number,
            func.sum(QuestionT1.num_of_marks)
            .filter(ResponseT1.is_correct == True)
            .label("correct_marks"),
            func.sum(QuestionT1.num_of_marks).label("possible_marks"),
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
            func.sum(QuestionT2.num_of_marks).label("possible_marks"),
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

    # UNION: https://docs.sqlalchemy.org/en/14/orm/query.html
    all_values = attempt_totals_t1.union_all(attempt_totals_t2)

    results_list = []

    # Make list of dictionaries holding relevant IDs and summations of correct marks
    for row in all_values:
        marks_dict = {}
        user_id = row[0]
        module_id = row[1]
        assessment_id = row[2]
        lecturer_id = row[3]
        attempt_number = row[4]
        correct_marks = row[5] if row[5] is not None else 0
        possible_marks = row[6]
        for entry in results_list:
            if (
                entry["user_id"] == user_id
                and entry["module_id"] == module_id
                and entry["assessment_id"] == assessment_id
                and entry["attempt_number"] == attempt_number
            ):
                entry["correct_marks"] += correct_marks
        else:
            marks_dict["user_id"] = user_id
            marks_dict["module_id"] = user_id
            marks_dict["assessment_id"] = assessment_id
            marks_dict["lecturer_id"] = lecturer_id
            marks_dict["attempt_number"] = attempt_number
            marks_dict["correct_marks"] = correct_marks
            marks_dict["possible_marks"] = possible_marks
            results_list.append(marks_dict)

    # Add a "highest_value" attribute for if this attempt is the HIGHEST scoring attempt the user has made
    for row in results_list:
        row["highest_value"] = True
        for comparison in results_list:
            if (
                row is not comparison
                and row["user_id"] == comparison["user_id"]
                and row["module_id"] == comparison["module_id"]
                and row["assessment_id"] == comparison["assessment_id"]
            ):
                if comparison["correct_marks"] > row["correct_marks"]:
                    row["highest_value"] = False
    # pprint(results_list)
    return results_list


def get_all_response_details():
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
            ResponseT1,
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
        output_dict["q_id"] = question[2]
        output_dict["question_text"] = question[3]
        output_dict["question_difficulty"] = question[4]
        output_dict["answer_given"] = question[5]
        output_dict["is_correct"] = question[6]
        output_dict["lecturer_id"] = question[7]
        output_dict["num_of_marks"] = question[8]
        output_dict["module_id"] = question[9]
        output_dict["assessment_id"] = question[10]
        output_dict["question_type"] = 1

        for answer in table_of_correct_t1_answers:
            if answer.q_t1_id == output_dict["q_id"]:
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
        output_dict["User_id"] = question[0]
        output_dict["attempt_number"] = question[1]
        output_dict["q_id"] = question[2]
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

        ## ADD FEEDBACK/FEEDFORWARD IF CORRECT/INCORRECT
        output_dict["feedback"] = (
            question[12] if output_dict["is_correct"] else question[13]
        )
        output_dict["feedforward"] = (
            question[14] if output_dict["is_correct"] else question[15]
        )
        t2_output.append(output_dict)

    final_output = t1_output + t2_output

    return final_output
