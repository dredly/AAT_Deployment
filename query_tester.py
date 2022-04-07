from aat import db, app
from aat.models import *
from aat.db_utils import get_all_assessment_marks
from pprint import pprint
from sqlalchemy import (
    select,
    func,
)  # https://docs.sqlalchemy.org/en/14/core/functions.html?highlight=func#module-sqlalchemy.sql.functions


with app.app_context():
    ...
