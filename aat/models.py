from email.policy import default
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class QuestionT2(db.Model):
    __tablename__ = "QuestionT2"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    weighting = db.Column(db.Integer, nullable=False)
    assessment_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Question id={self.id} on assessment id={self.assessment_id}"

class QuestionT1(db.Model):
    __tablename__ = "QuestionT1"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    weighting = db.Column(db.Integer, nullable=False)
    option_id = db.relationship('AnswersT1', backref='questiont1', lazy=True)
    assessment_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Question id={self.id} on assessment id={self.assessment_id}"


class AnswersT1(db.Model):
    __tablename__ = "AnswersT1"
    id = db.Column(db.Integer, primary_key=True)
    questiont1_id = db.Column(db.Integer, db.ForeignKey(QuestionT1.id), nullable=False)
    answer_texts = db.Column(db.Text, nullable=False)
    assessment_id = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Question id={self.id} on assessment id={self.assessment_id}"

