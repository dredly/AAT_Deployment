from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Assessment(db.Model):
    __tablename__ = "Assessment"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    questiont2 = db.relationship("QuestionT2", backref="assessment", lazy=True)

    def __repr__(self):
        return f"Assessment - {self.title}"


class QuestionT2(db.Model):
    __tablename__ = "QuestionT2"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    weighting = db.Column(db.Integer, nullable=False)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("Assessment.id"), nullable=False
    )

    def __repr__(self):
        return f"Question id={self.id} on assessment id={self.assessment_id}"

# temporary while waiting for model 

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def password(self):
        raise AttributeError("Password is not readable.") 

    @password.setter
    def password(self, password):
        self.hashed_password=generate_password_hash(password)        

    def verify_password(self, password): 
        return check_password_hash(self.hashed_password, password)

    def __repr__(self): 
        return f"User: {self.name}"
