import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db, QuestionT2, QuestionT1, AnswersT1
from .assessments import assessments
from .auth import auth
from .stats import stats
from .legendary_gamification import legendary_gamification

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "aat.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(assessments, url_prefix="/assessments")
app.register_blueprint(stats, url_prefix="/stats")
app.register_blueprint(legendary_gamification, url_prefix="/legendary_gamification")
app.register_blueprint(auth)

db.init_app(app)
