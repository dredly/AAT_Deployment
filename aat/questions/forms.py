from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, IntegerRangeField, SubmitField
from wtforms.validators import DataRequired


class QuestionT2Form(FlaskForm):
    question_text = TextAreaField(
        "Enter question text", default="", validators=[DataRequired()]
    )
    correct_answer = TextAreaField(
        "Enter the correct answer", validators=[DataRequired()]
    )
    num_of_marks = IntegerField("How many marks?", validators=[DataRequired()])
    difficulty = IntegerRangeField("Select a difficulty from 1 to 3 (1 being easiest)")
    feedback_if_correct = TextAreaField(
        "Enter feedback to be shown if answered correctly", validators=[DataRequired()]
    )
    feedback_if_wrong = TextAreaField(
        "Enter feedback to be shown if answered incorrectly",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add question")
