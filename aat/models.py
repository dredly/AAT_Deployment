from flask_sqlalchemy import SQLAlchemy

# First trying to get it working without model inheritance

db = SQLAlchemy()

# Format for model: primary key, then all foreign keys, then all other columns, then all relationships


class Assessment(db.Model):
    __tablename__ = "Assessment"
    assessment_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys --- CONTAINS PLACEHOLDERS
    module_id = db.Column(db.Integer, nullable=False)
    staff_id = db.Column(db.Integer, nullable=False)
    # --- Other Columns ---
    title = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.DateTime)
    time_limit = db.Column(db.Integer)  # Time limit in seconds
    num_of_credits = db.Column(db.Integer, nullable=False, default=0)
    is_summative = db.Column(db.Boolean, nullable=False, default=False)
    # --- Relationships --- TODO


# class QuestionT1(db.Model):
#     pass

# class QuestionT2(db.Model):
#     pass

# class Option(db.Model):
#     pass

# class Module(db.Model):
#     pass

# class Student(db.Model):
#     pass

# class Staff(db.Model):
#     pass

# class TakesAssessment(db.Model):
#     pass

# class ResponseT1(db.Model):
#     pass

# class ResponseT2(db.Model):
#     pass
