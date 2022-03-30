from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField
from ..models import User

class QuestionForm(FlaskForm):
    question = StringField("Question")
    options = RadioField("Options", choices=[""])




class ChallengeForm(FlaskForm):
    difficulty = SelectField("Difficulty", choices=[1, 2, 3])