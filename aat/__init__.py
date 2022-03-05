from flask import Flask
from .assessments import assessments
from .auth import auth
from .stats import stats
from .legendary_gamification import legendary_gamification

app = Flask(__name__)

app.register_blueprint(assessments, url_prefix="/assessments")
app.register_blueprint(stats, url_prefix="/stats")
app.register_blueprint(legendary_gamification, url_prefix="/legendary_gamification")
app.register_blueprint(auth)
