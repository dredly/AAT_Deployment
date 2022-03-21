import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import (
    db,
    login_manager,
    Assessment,
    QuestionT1,
    QuestionT2,
    Option,
    Module,
    TakesAssessment,
    ResponseT1,
    ResponseT2,
    User,
    Role,
    Permission,
)
from .assessments import assessments
from .auth import auth
from .stats import stats
from .student_stats import student_stats

# Admin
from flask_admin import Admin
from .views import AdminView

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "aat.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Make sure to install python-dotenv, and check the .env.example file
# Then simply make your own .env file with the same format
# app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SECRET_KEY"] = "a secret key"

app.register_blueprint(assessments, url_prefix="/assessments")
app.register_blueprint(stats, url_prefix="/stats")
app.register_blueprint(student_stats, url_prefix="/student-stats")
app.register_blueprint(auth)

db.init_app(app)
login_manager.init_app(app)

from . import routes

# ADMIN
admin = Admin(app=app, name="Admin Panel", template_mode="bootstrap3")
admin.add_views(
    AdminView(Assessment, db.session),
    AdminView(QuestionT1, db.session),
    AdminView(QuestionT2, db.session),
    AdminView(Option, db.session),
    AdminView(Module, db.session),
    AdminView(TakesAssessment, db.session),
    AdminView(ResponseT1, db.session),
    AdminView(ResponseT2, db.session),
    AdminView(User, db.session),
    AdminView(Role, db.session),
)
# Now accessible through /admin/
