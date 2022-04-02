from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():
    # ALL MODULES AND ASSESSMENTS
    all_modules_and_assessments = (
        db.session.query(User, Assessment, Module)
        .with_entities(Module.title, Assessment.title)
        .select_from(User)
        .join(Assessment)
        .join(Module)
        .group_by(Module.title)
        .group_by(Assessment.title)
    ).all()

    pprint(f"{all_modules_and_assessments=}")

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

    # module_query = q.with_entities(Module.title).group_by(Module.title).all()

    # assessment_query = (
    #     q.with_entities(Assessment.title).group_by(Assessment.title).all()
    # )
    # marks_query = db.engine.execute(User.select())

    # marks_query = db.engine.execute(select(func.count()).select_from(q))

    # print(module_query)
    # print(assessment_query)

    # print(q)

    # list_of_modules = q.group_by(Module.title).all()
    # pprint(list_of_modules)

    # q_as_list_of_dict = [r._asdict() for r in q]

    # pprint(q_as_list_of_dict)
