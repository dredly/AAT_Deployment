from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    IntegerField,
    SubmitField,
    SelectMultipleField,
    IntegerRangeField,
)
from wtforms.validators import DataRequired


class DeleteQuestionsForm(FlaskForm):
    questions_to_delete = SelectMultipleField(
        "Select questions to delete",
        # Choices starts off empty, as it is populated dynamically
        # based on the questions on a particular assessment
        choices=[],
    )
    submit = SubmitField("Delete selected questions")


class AnswerType2Form(FlaskForm):
    answer = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("Submit Answer")
