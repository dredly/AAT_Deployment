from aat import db, app
from aat.models import *
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions

with app.app_context():

    print(get_total_marks_each_assessment_is_worth())
