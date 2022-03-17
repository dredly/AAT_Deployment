import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db, QuestionT2
from .assessments import assessments
from .auth import auth
from .stats import stats
from .student_stats import student_stats

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "aat.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "NOTSECUREINEEDTOCHANGETHISASAP"

app.register_blueprint(assessments, url_prefix="/assessments")
app.register_blueprint(stats, url_prefix="/stats")
app.register_blueprint(student_stats, url_prefix="/student-stats")
app.register_blueprint(auth)

db.init_app(app)

from . import routes
