from flask_wtf import FlaskForm
from wtforms.fields import DateField
from wtforms.validators import NumberRange
from wtforms import (
    TextAreaField,
    IntegerField,
    SubmitField,
    SelectMultipleField,
    BooleanField,
    SelectField
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
    module_id= IntegerField("Enter module ID",validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    due_date = DateField(
        "Enter the due date", format='%Y-%m-%d')
    num_of_credits = IntegerField("Enter Assessment Credits", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    time_limit = IntegerField("Enter time limit in minutes", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    is_summative = BooleanField()
    submit = SubmitField("Create Assessment")

class DeleteAssessmentForm(FlaskForm):
    submit = SubmitField("Confirm")
    cancel = SubmitField("Cancel")

class EditAssessmentForm(FlaskForm):
    title = TextAreaField(
        "Enter Title", default="", validators=[DataRequired()]
    )
    module_id= IntegerField("Enter module ID",validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    due_date = DateField(
        "Enter the due date", format='%Y-%m-%d')
    num_of_credits = IntegerField("Enter Assessment Credits", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    time_limit = IntegerField("Enter time limit in minutes", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    is_summative = BooleanField()
    submit = SubmitField("Done")

class RemoveQuestionForm(FlaskForm):
    submit = SubmitField("Remove")
    cancel = SubmitField("Cancel")

class AddQuestionFilterForm(FlaskForm):
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

