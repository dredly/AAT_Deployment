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


def get_assessment_id_and_total_marks_possible():
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
    return assessment_id_and_total_marks_possible


def get_all_assessment_marks(
    input_user_id=None,
    input_lecturer_id=None,
    input_module_id=None,
    input_assessment_id=None,
    highest_scoring_attempt_only=False,
    debug=False,
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

    Optional filters added for student, lecturer, module and assessment id
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

    print("****")
    print(f"{assessment_id_and_total_marks_possible=}") if debug else ...
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

            final_output.append(marks_dict)

    # POSSIBLE MARKS NOT CORRECT - work out separately then add on?

    if debug:
        print("***")
        pprint(f"final_output_before_highest_flag=")
        pprint(final_output)

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

    if debug:
        print("***")
        pprint(f"{final_output=}")

    return final_output


########################################################################


def get_all_response_details(
    input_user_id=None,
    input_lecturer_id=None,
    input_module_id=None,
    input_assessment_id=None,
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

    return final_output
