from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():
    """
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
    attempt_totals_t2 = (
        db.session.query(User, QuestionT2, ResponseT2, Module, Assessment)
        .with_entities(
            User,
            Module.title,
            ResponseT2.attempt_number,
            func.sum(QuestionT2.num_of_marks).filter(ResponseT2.is_correct == True),
            func.sum(QuestionT2.num_of_marks),
        )
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .group_by(User)
        .group_by(ResponseT2.attempt_number)
        .all()
    )

    pprint(attempt_totals_t2)

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
