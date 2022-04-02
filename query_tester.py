from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():
    """
    Combines Q1 and Q2 question types into one table of FUN
    - user_id
    - attempt_id
    - question_id
    - t1_or_t2
    - response
    - was_it_correct
    - correct_answer
    - marks_awarded
    - assessment_id
    - module_id
    - lecturer_id
    - difficulty
    - feedback (right/wrong)
    - feedforward (right/wrong)
    """

    # TYPE 1

    question_totals_t1 = (
        db.session.query(User, QuestionT1, ResponseT1, Option, Module, Assessment)
        .with_entities(
            User.id,
            ResponseT1.attempt_number,
            QuestionT1.q_t1_id,
            QuestionT1.question_text,
            QuestionT1.difficulty,
            Option.option_text,
            ResponseT1.is_correct,
            Assessment.lecturer_id,
            QuestionT1.num_of_marks,
            Module.module_id,
            Assessment.assessment_id,
            # The correct answer - think it's easier to add later?
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

    # Should be able to do this as a join but not working
    t1_output = []
    for question in question_totals_t1:
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
        output_dict["question_type"] = 1

        for answer in table_of_correct_t1_answers:
            if answer.q_t1_id == output_dict["q_id"]:
                output_dict["correct_answer_text"] = answer.option_text

        t1_output.append(output_dict)

    # pprint(t1_output)

    # TYPE 2

    question_totals_t2 = (
        db.session.query(User, QuestionT2, ResponseT2, Option, Module, Assessment)
        .with_entities(
            User.id,
            ResponseT2.attempt_number,
            QuestionT2.q_t2_id,
            QuestionT2.question_text,
            QuestionT2.difficulty,
            ResponseT2.response_content,
            ResponseT2.is_correct,
            Assessment.lecturer_id,
            QuestionT2.num_of_marks,
            Module.module_id,
            Assessment.assessment_id,
            QuestionT2.correct_answer,
            # The correct answer - think it's easier to add later?
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
    # pprint(question_totals_t2.all())

    # table_of_correct_t2_answers = Option.query.filter(Option.is_correct == True)

    # # Should be able to do this as a join but not working
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
        output_dict["question_type"] = 10
        output_dict["correct_answer_text"] = question[11]

        t2_output.append(output_dict)

    # pprint(t2_output)

    final_output = t1_output + t2_output

    pprint(final_output)
