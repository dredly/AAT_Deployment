from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField 
from wtforms.validators import DataRequired, EqualTo 

class RegistrationForm(FlaskForm): 
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), 
        EqualTo('password_check')])
    password_check = PasswordField('Confirm Password', validators=[DataRequired()])
    admin = BooleanField('Lecturer')
    submit = SubmitField('Register')

class LoginForm(FlaskForm): 
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')