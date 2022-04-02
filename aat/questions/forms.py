from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    IntegerField,
    IntegerRangeField,
    SubmitField,
    SelectField,
    RadioField,
)
from wtforms.validators import DataRequired, NumberRange


class QuestionT1Form(FlaskForm):
    question_text = TextAreaField(
        "Enter question text", default="", validators=[DataRequired()]
    )
    option_a = TextAreaField("Please enter option a", validators=[DataRequired()])
    option_b = TextAreaField("Please enter option b", validators=[DataRequired()])
    option_c = TextAreaField("Please enter option c", validators=[DataRequired()])
    correct_option = RadioField(
        "Correct Option",
        choices=[(0, "option a"), (1, "option b"), (2, "option c")],
        validators=[DataRequired()],
    )
    tag = SelectField("Select a tag for the question.", choices=[])
    num_of_marks = IntegerField(
        "How many marks?", validators=[DataRequired(), NumberRange(min=0)]
    )
    difficulty = IntegerRangeField("Select a difficulty from 1 to 3 (1 being easiest)")
    feedback_if_correct = TextAreaField(
        "Enter feedback to be shown if answered correctly", validators=[DataRequired()]
    )
    feedback_if_wrong = TextAreaField(
        "Enter feedback to be shown if answered incorrectly",
        validators=[DataRequired()],
    )
    feedforward_if_correct = TextAreaField(
        "Enter feedforward to be shown if answered correctly",
        validators=[DataRequired()],
    )
    feedforward_if_wrong = TextAreaField(
        "Enter feedforward to be shown if answered incorrectly",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add question")


class FilterForm(FlaskForm):
    filter = SelectField(
        "Filter questions by:",
        choices=[
            ("all", "Show all"),
            ("type1", "Type 1 (multiple choice)"),
            ("type2", "Type 2 (written answer)"),
            ("floating", "Unassigned"),
            ("assigned", "Assigned"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update")


class QuestionT2Form(FlaskForm):
    question_text = TextAreaField(
        "Enter question text", default="", validators=[DataRequired()]
    )
    correct_answer = TextAreaField(
        "Enter the correct answer", validators=[DataRequired()]
    )
    tag = SelectField("Select a tag for the question.", choices=[])
    num_of_marks = IntegerField(
        "How many marks?", validators=[DataRequired(), NumberRange(min=0)]
    )
    difficulty = IntegerRangeField("Select a difficulty from 1 to 3 (1 being easiest)")
    feedback_if_correct = TextAreaField(
        "Enter feedback to be shown if answered correctly", validators=[DataRequired()]
    )
    feedback_if_wrong = TextAreaField(
        "Enter feedback to be shown if answered incorrectly",
        validators=[DataRequired()],
    )
    feedforward_if_correct = TextAreaField(
        "Enter feedforward to be shown if answered correctly",
        validators=[DataRequired()],
    )
    feedforward_if_wrong = TextAreaField(
        "Enter feedforward to be shown if answered incorrectly",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add question")


class DeleteForm(FlaskForm):
    submit = SubmitField("Yes, delete")
