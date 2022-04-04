import os
from dotenv import load_dotenv
from flask import Flask, session, render_template

# from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from .models import *
from .assessments import assessments
from .questions import questions
from .auth import auth
from .staff_stats import staff_stats
from .student_stats import student_stats
from .legendary_gamification import legendary_gamification

# Admin
from flask_admin import Admin
from .views import AdminView

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

# Error handling
# - Rich: I would rather have put  this in errors.py but getting circular errors
#       (I mean, it works but still, not ideal)
def page_not_found(e):
    return render_template("error_handling/404.html"), 404


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "aat.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Make sure to install python-dotenv, and check the .env.example file
# Then simply make your own .env file with the same format
# app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SECRET_KEY"] = "a secret key"

app.register_blueprint(assessments, url_prefix="/assessments")
app.register_blueprint(questions, url_prefix="/questions")
app.register_blueprint(legendary_gamification, url_prefix="/legendary_gamification")
app.register_blueprint(staff_stats, url_prefix="/staff-stats")
app.register_blueprint(student_stats, url_prefix="/student-stats")
app.register_blueprint(auth)
app.register_error_handler(404, page_not_found)

db.init_app(app)
login_manager.init_app(app)

from . import routes

# ADMIN
admin = Admin(app=app, name="Admin Panel", template_mode="bootstrap3")
admin.add_views(
    AdminView(Assessment, db.session),
    AdminView(Tag, db.session),
    AdminView(QuestionT1, db.session),
    AdminView(QuestionT2, db.session),
    AdminView(Option, db.session),
    AdminView(Module, db.session),
    AdminView(ResponseT1, db.session),
    AdminView(ResponseT2, db.session),
    AdminView(User, db.session),
    AdminView(Role, db.session),
    AdminView(Challenge, db.session),
    AdminView(ChallengeQuestions, db.session),
    AdminView(Tier, db.session),
    AdminView(Badge, db.session),
    AdminView(Achievement, db.session),
    AdminView(Awarded_Badge, db.session),
    AdminView(Awarded_Achievement, db.session),
)
# Now accessible through /admin/

# Context Processor to make Permission variables available to templates
@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)
