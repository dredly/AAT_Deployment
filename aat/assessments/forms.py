from flask_wtf import FlaskForm
from wtforms.fields import DateField
from wtforms.validators import NumberRange
from wtforms import (
    TextAreaField,
    IntegerField,
    SubmitField,
    SelectMultipleField,
    BooleanField,
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

class AssessmentForm(FlaskForm):
    
    title = TextAreaField(
        "Enter Title", default="", validators=[DataRequired()]
    )
    due_date = DateField(
        "Enter the due date", format='%Y-%m-%d')
    num_of_credits = IntegerField("How many credits?", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    time_limit = IntegerField("Enter time limit in minutes", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    is_summative = BooleanField()
    submit = SubmitField("Add Assessment")

class DeleteAssessmentForm(FlaskForm):
    submit = SubmitField("Confirm")
    cancel = SubmitField("Cancel")

class EditAssessmentForm(FlaskForm):
    title = TextAreaField(
        "Enter Title", default="", validators=[DataRequired()]
    )
    due_date = DateField(
        "Enter the due date", format='%Y-%m-%d')
    num_of_credits = IntegerField("How many credits?", validators=[DataRequired()])
    time_limit = IntegerField("Enter time limit in minutes")
    is_summative = BooleanField()
    submit = SubmitField("Edit Assessment")

