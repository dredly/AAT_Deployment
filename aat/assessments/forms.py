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

class AnswerType1Form(FlaskForm):
    chosen_option = RadioField('Answer Options')
    submit = SubmitField("Submit Answer")

class AnswerType2Form(FlaskForm):
    answer = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("Submit Answer")


# CRUD Assessment forms


class AssessmentForm(FlaskForm):
    title = TextAreaField("Enter Title", default="", validators=[DataRequired()])
    module_id= IntegerField("Enter module ID",validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    due_date = DateField("Enter the due date", format='%Y-%m-%d')
    num_of_credits = IntegerField("Enter Assessment Credits", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    time_limit = IntegerField("Enter time limit in minutes", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    is_summative = BooleanField("Select if Assessment is summative")
    submit = SubmitField("Add Questions")


    def validate_on_submit(self):
            result = super(AssessmentForm, self).validate()
            print(date.today)
            if (self.due_date.data < date.today()):
                return False
            else:
                return result


class DeleteAssessmentForm(FlaskForm):
    submit = SubmitField("Confirm")
    cancel = SubmitField("Cancel")

class EditAssessmentForm(FlaskForm):
    title = TextAreaField("Enter Title", default="", validators=[DataRequired()])
    module_id= IntegerField("Enter module ID",validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    due_date = DateField("Enter the due date", format='%Y-%m-%d')
    num_of_credits = IntegerField("Enter Assessment Credits", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    time_limit = IntegerField("Enter time limit in minutes", validators=[NumberRange(min=0, message='Must enter a number greater than 0')])
    is_summative = BooleanField("Select if Assessment is summative")
    submit = SubmitField("Add Questions")

class RemoveQuestionForm(FlaskForm):
    submit = SubmitField("Remove")
    cancel = SubmitField("Cancel")

class AddQuestionToAssessmentForm(FlaskForm):
    add = SubmitField(label="Add to Assessment")

class CreateQuestionT1Form(FlaskForm):
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

class FinishForm(FlaskForm):
    finish = SubmitField(label="Finish")
