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
        .group_by(ResponseT1.attempt_number)
    )

    attempt_totals_t2 = (
        db.session.query(User, QuestionT2, ResponseT2, Module, Assessment)
        .with_entities(
            User.id,
            Module.module_id,
            Assessment.assessment_id,
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
        attempt_number = row[3]
        correct_marks = row[4] if row[4] is not None else 0
        possible_marks = row[5]
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
