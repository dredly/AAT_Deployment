from flask_sqlalchemy import SQLAlchemy

# First trying to get it working without model inheritance

db = SQLAlchemy()

# Format for model: primary key, then all foreign keys, then all other columns, then all relationships


class Assessment(db.Model):
    __tablename__ = "Assessment"
    assessment_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys --- CONTAINS PLACEHOLDERS
    module_id = db.Column(db.Integer, db.ForeignKey("Module.module_id"), nullable=False)
    staff_id = db.Column(db.Integer, nullable=False)
    # --- Other Columns ---
    title = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.DateTime)
    time_limit = db.Column(db.Integer)  # Time limit in seconds
    num_of_credits = db.Column(db.Integer, nullable=False, default=0)
    is_summative = db.Column(db.Boolean, nullable=False, default=False)
    # --- Relationships --- TODO: add more as tables are added to the db
    question_t2 = db.relationship("QuestionT2", backref="assessment", lazy=True)


class QuestionT1(db.Model):
    __tablename__ = "QuestionT1"
    q_t1_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("Assessment.assessment_id"), nullable=False
    )
    # --- Other Columns ---
    num_of_marks = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)


class QuestionT2(db.Model):
    __tablename__ = "QuestionT2"
    q_t2_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("Assessment.assessment_id"), nullable=False
    )
    # --- Other Columns ---
    num_of_marks = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)


# class Option(db.Model):
#     pass


class Module(db.Model):
    __tablename__ = "Module"
    module_id = db.Column(db.Integer, primary_key=True)
    # --- Other Columns ---
    title = db.Column(db.String(120), unique=True, nullable=False)
    total_credits = db.Column(db.Integer, nullable=False)
    # --- Relationship ---
    assessments = db.relationship("Assessment", backref="module", lazy=True)


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
