from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():

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
            assessment_id_and_total_marks_possible[
                q.assessment_id
            ] = total_marks_possible
        return assessment_id_and_total_marks_possible

    def get_module_ids_with_total_credits_and_total_marks_possible():
        q = Module.query.all()
        output_dict = {}
        for module in q:
            output_dict[module.module_id] = {
                "total_num_of_credits": 0,
                "total_marks_possible": 0,
            }
            # Find all assessments connected
            for assessment in module.assessments:
                output_dict[module.module_id][
                    "total_num_of_credits"
                ] += assessment.num_of_credits

                # Q1
                for q1 in assessment.question_t1:
                    output_dict[module.module_id][
                        "total_marks_possible"
                    ] += q1.num_of_marks
                # Q2
                for q2 in assessment.question_t2:
                    output_dict[module.module_id][
                        "total_marks_possible"
                    ] += q2.num_of_marks

                # Will then need to go through the question types
        return output_dict

    print(get_module_ids_with_total_credits_and_total_marks_possible())
