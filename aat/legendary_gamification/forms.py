from tokenize import String
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField

class QuestionForm(FlaskForm):
    question = StringField("Question")
    options = RadioField("Options", choices=[""])