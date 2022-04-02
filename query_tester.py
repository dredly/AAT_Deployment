from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():
    """
    Returns list of dictionaries, each dictionary has the following keys:
        - 'user_id' (int)
        - 'module_id' (int)
        - 'assessment_id' (int)
        - 'attempt_number' (int)
        - 'correct_marks' (int)
        - 'possible_marks' (int)
        - 'highest_value' (bool)

    STEP ONE:
    - Get sum of marks (T1 & T2) for all attempts, then mark which attempt scored highest.
    - If multiple versions score highest then first one is kept.

    SPLIT by T1 T2
    Calculate attempt totals:
    - Grouped by
        - User ID
        - Assessment ID
        - Module ID
    - Values
        - Total marks
        - Possible marks
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
    pprint(results_list)

    """
    # ALL MODULES AND ASSESSMENTS
    all_modules_and_assessments = (
        db.session.query(User, Assessment, Module)
        .with_entities(
            Module,
            Assessment,
        )
        .select_from(User)
        .join(Assessment)
        .join(Module)
        .group_by(Module.title)
        .group_by(Assessment.title)
        .all()
    )

    # HA responses. Fucksake Lins. Can we put "highest scoring attempt"?

    q_response_t1 = db.session.query()

    # To calculate average marks we need to combine T1 with T2

    # query = db.select([db.func.round(db.func.sum(STUDENTS.c.percentage), 2)])

    # pprint(f"{all_modules_and_assessments=}")

    for item in all_modules_and_assessments:
        result = item._asdict()
        print(result)
    """
    """
    # USER-FILTERED QUERIES
    user_id = 4
    base_query = (
        db.session.query(User, ResponseT2, QuestionT2, Assessment, Module)
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .join(Module)
        .filter(User.id == user_id)
    )

    marks_query = (
        base_query.with_entities(
            Module.title,
            Assessment.title,
            ResponseT2.attempt_number,
            func.sum(QuestionT2.num_of_marks).filter(ResponseT2.is_correct == True),
            func.sum(QuestionT2.num_of_marks),
        )
        .group_by(Module.title)
        .group_by(Assessment.title)
        .group_by(ResponseT2.attempt_number)
    ).all()

    pprint(f"{marks_query=}")
    """

    """
    # ALL MODULES AND ASSESSMENTS
    all_modules_and_assessments = (
        db.session.query(User, Assessment, Module)
        .with_entities(
            Module,
            Assessment,
        )
        .select_from(User)
        .join(Assessment)
        .join(Module)
        .group_by(Module.title)
        .group_by(Assessment.title)
        .all()
    )

    # HA responses. Fucksake Lins. Can we put "highest scoring attempt"?

    q_response_t1 = db.session.query()

    # To calculate average marks we need to combine T1 with T2

    # query = db.select([db.func.round(db.func.sum(STUDENTS.c.percentage), 2)])

    # pprint(f"{all_modules_and_assessments=}")

    for item in all_modules_and_assessments:
        result = item._asdict()
        print(result)
    """
    """
    # USER-FILTERED QUERIES
    user_id = 4
    base_query = (
        db.session.query(User, ResponseT2, QuestionT2, Assessment, Module)
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .join(Module)
        .filter(User.id == user_id)
    )

    marks_query = (
        base_query.with_entities(
            Module.title,
            Assessment.title,
            ResponseT2.attempt_number,
            func.sum(QuestionT2.num_of_marks).filter(ResponseT2.is_correct == True),
            func.sum(QuestionT2.num_of_marks),
        )
        .group_by(Module.title)
        .group_by(Assessment.title)
        .group_by(ResponseT2.attempt_number)
    ).all()

    pprint(f"{marks_query=}")
    """
