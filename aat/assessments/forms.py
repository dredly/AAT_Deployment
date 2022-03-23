from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    IntegerField,
    SubmitField,
    SelectMultipleField,
    IntegerRangeField,
)
from wtforms.validators import DataRequired
from ..models import Assessment


class QuestionT2Form(FlaskForm):
    question_text = TextAreaField(
        "Enter question text", default="", validators=[DataRequired()]
    )
    correct_answer = TextAreaField(
        "Enter the correct answer", validators=[DataRequired()]
    )
    num_of_marks = IntegerField("How many marks?", validators=[DataRequired()])
    difficulty = IntegerRangeField("Select a difficulty from 1 to3 (1 being easiest)")
    feedback_if_correct = TextAreaField(
        "Enter feedback to be shown if answered correctly", validators=[DataRequired()]
    )
    feedback_if_wrong = TextAreaField(
        "Enter feedback to be shown if answered incorrectly",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add question")


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
