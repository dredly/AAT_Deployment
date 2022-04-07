from flask_wtf import FlaskForm
from wtforms.fields import DateField, RadioField
from wtforms.validators import NumberRange
from datetime import date
from wtforms import (
    TextAreaField,
    IntegerField,
    IntegerRangeField,
    SubmitField,
    SelectMultipleField,
    BooleanField,
    SelectField,
)
from wtforms.validators import DataRequired, ValidationError


from aat.models import Assessment, Module

# STOLEN from Linsey's "DeleteQuestionsForm"
# because Linsey is The Python Queen
class SelectModuleForm(FlaskForm):
    module_to_select = SelectMultipleField(
        "Select module",
        choices=[],
    )
    submit = SubmitField("Select Assessment")
    # ...but then chickened out as this is just a QOL thing rather than a functional thing.
