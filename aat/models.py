from flask_sqlalchemy import SQLAlchemy

#First trying to get it working without model inheritance

db = SQLAlchemy()

class Assessment(db.model):
    pass

class QuestionT1(db.model):
    pass

class QuestionT2(db.model):
    pass

class Option(db.model):
    pass

class Module(db.model):
    pass

class Student(db.model):
    pass

class Staff(db.model):
    pass

class TakesAssessment(db.model):
    pass

class ResponseT1(db.model):
    pass

class ResponseT2(db.model):
    pass


# class Assessment(db.Model):
#     __tablename__ = "Assessment"
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(120), nullable=False)
#     questiont2 = db.relationship("QuestionT2", backref="assessment", lazy=True)

#     def __repr__(self):
#         return f"Assessment - {self.title}"


# class QuestionT2(db.Model):
#     __tablename__ = "QuestionT2"
#     id = db.Column(db.Integer, primary_key=True)
#     question_text = db.Column(db.Text, nullable=False)
#     correct_answer = db.Column(db.Text, nullable=False)
#     weighting = db.Column(db.Integer, nullable=False)
#     assessment_id = db.Column(
#         db.Integer, db.ForeignKey("Assessment.id"), nullable=False
#     )

#     def __repr__(self):
#         return f"Question id={self.id} on assessment id={self.assessment_id}"
