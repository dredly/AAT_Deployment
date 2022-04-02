from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():
    user_id = 4
    q = (
        db.session.query(User, ResponseT2, QuestionT2, Assessment, Module)
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .join(Module)
        .filter(User.id == user_id)
    )

    possible_marks_query = (
        q.with_entities(
            Module.title,
            Assessment.title,
            ResponseT2.attempt_number,
            func.sum(QuestionT2.num_of_marks),
        )
        .group_by(Module.title)
        .group_by(Assessment.title)
        .group_by(ResponseT2.attempt_number)
    )

    correct_marks_query = possible_marks_query.filter(ResponseT2.is_correct == True)

    pprint(possible_marks_query.all())
    pprint(correct_marks_query.all())

    module_query = q.with_entities(Module.title).group_by(Module.title).all()

    assessment_query = (
        q.with_entities(Assessment.title).group_by(Assessment.title).all()
    )
    # marks_query = db.engine.execute(User.select())

    # marks_query = db.engine.execute(select(func.count()).select_from(q))

    # print(module_query)
    # print(assessment_query)

    # print(q)

    # list_of_modules = q.group_by(Module.title).all()
    # pprint(list_of_modules)

    # q_as_list_of_dict = [r._asdict() for r in q]

    # pprint(q_as_list_of_dict)
