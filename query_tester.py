from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():

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
                item
                for item in final_output
                if item["lecturer_id"] == input_lecturer_id
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

    pprint(get_all_response_details(input_user_id=1))
