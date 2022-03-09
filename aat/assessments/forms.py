from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from ..models import QuestionT2, Assessment


class NewQuestionForm(FlaskForm):
    question_text = TextAreaField("Enter question text", validators=[DataRequired()])
    correct_answer = TextAreaField(
        "Enter the correct answer", validators=[DataRequired()]
    )
    weighting = IntegerField("Select a weighting", validators=[DataRequired()])
    submit = SubmitField("Add question")
