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
