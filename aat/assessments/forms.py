from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired
from ..models import QuestionT2, Assessment


class QuestionForm(FlaskForm):
    question_text = TextAreaField(
        "Enter question text", default="", validators=[DataRequired()]
    )
    correct_answer = TextAreaField(
        "Enter the correct answer", validators=[DataRequired()]
    )
    weighting = IntegerField("Select a weighting", validators=[DataRequired()])
    submit = SubmitField("Add question")


class DeleteQuestionsForm(FlaskForm):
    questions_to_delete = SelectMultipleField(
        "Select questions to delete",
        # Choices starts off empty, as it is populated dynamically
        # based on the questions on a particular assessment
        choices=[],
    )
    submit = SubmitField("Delete selected questions")
