from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask_login import LoginManager

# First trying to get it working without model inheritance

db = SQLAlchemy()
login_manager = LoginManager()

# Format for model: primary key, then all foreign keys, then all other columns, then all relationships

class ResponseT2(db.Model): 
    __tablename__ = "t2_responses"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('Assessment.assessment_id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('QuestionT2.q_t2_id'), primary_key=True)
    response_content = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
class Assessment(db.Model):
    __tablename__ = "Assessment"
    assessment_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys --- CONTAINS PLACEHOLDERS
    module_id = db.Column(db.Integer, db.ForeignKey("Module.module_id"), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # --- Other Columns ---
    title = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.DateTime)
    time_limit = db.Column(db.Integer)  # Time limit in seconds
    num_of_credits = db.Column(db.Integer, nullable=False, default=0)
    is_summative = db.Column(db.Boolean, nullable=False, default=False)
    # --- Relationships --- TODO: add more as tables are added to the db
    question_t1 = db.relationship("QuestionT1", backref="assessment", lazy=True)
    question_t2 = db.relationship("QuestionT2", backref="assessment", lazy=True)
    responses_t2 = db.relationship("ResponseT2", foreign_keys=[ResponseT2.assessment_id],
                                        backref=db.backref('assessment', lazy='joined'),
                                        lazy='dynamic', 
                                        cascade='all, delete-orphan'
                                        )
    # takes_assessment = db.relationship(
    #     "TakesAssessment", backref="assessment", lazy=True
    # )


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
    # --- Relationships ---
    option = db.relationship("Option", backref="questiont1", lazy=True)


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
    responses = db.relationship('ResponseT2', 
                                    foreign_keys=[ResponseT2.question_id],
                                    backref=db.backref('question', lazy='joined'),
                                    lazy='dynamic', 
                                    cascade='all, delete-orphan'
                                    )


class Option(db.Model):
    __tablename__ = "Option"
    # --- Foreign Keys ---
    option_id = db.Column(db.Integer, primary_key=True)
    q_t1_id = db.Column(db.Integer, db.ForeignKey("QuestionT1.q_t1_id"), nullable=False)
    # ---- Other Columns ---
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)


class Module(db.Model):
    __tablename__ = "Module"
    module_id = db.Column(db.Integer, primary_key=True)
    # --- Other Columns ---
    title = db.Column(db.String(120), unique=True, nullable=False)
    total_credits = db.Column(db.Integer, nullable=False)
    # --- Relationships ---
    assessment = db.relationship("Assessment", backref="module", lazy=True)


# class TakesAssessment(db.Model):
#     __tablename__ = "TakesAssessment"
#     takes_assessment_id = db.Column(db.Integer, primary_key=True)
#     # --- Foreign Keys ---
#     student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#     assessment_id = db.Column(
#         db.Integer, db.ForeignKey("Assessment.assessment_id"), nullable=False
#     )
#     # --- Relationships ---
#     response_t1 = db.relationship("ResponseT1", backref="takes_assessment", lazy=True)
#     response_t2 = db.relationship("ResponseT2", backref="takes_assessment", lazy=True)

#     def __repr__(self): 
#         return f"Assessment Completion {self.takes_assessment_id}: <Student: {self.student_id}> <Assessment: {self.assessment_id}>"


# class ResponseT1(db.Model):
#     __tablename__ = "ResponseT1"
#     response_t1_id = db.Column(db.Integer, primary_key=True)
#     # --- Foreign Keys ---
#     takes_assessment_id = db.Column(
#         db.Integer, db.ForeignKey("TakesAssessment.takes_assessment_id"), nullable=False
#     )
#     # --- Other Columns ---
#     response_content = db.Column(db.Integer, nullable=False)
#     correct = db.Column(db.Boolean, nullable=False)


# class ResponseT2(db.Model):
#     __tablename__ = "ResponseT2"
#     response_t2_id = db.Column(db.Integer, primary_key=True)
#     # --- Foreign Keys ---
#     takes_assessment_id = db.Column(
#         db.Integer, db.ForeignKey("TakesAssessment.takes_assessment_id"), nullable=False
#     )
#     t2_question_id = db.Column(db.Integer, db.ForeignKey("QuestionT2.q_t2_id"), nullable=False)
#     # --- Other Columns ---
#     response_content = db.Column(db.Text, nullable=False)
#     correct = db.Column(db.Boolean, nullable=False)



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    # --- Relationships ---
    assessment = db.relationship("Assessment", backref="user", lazy=True)
    # takes_assessment = db.relationship("TakesAssessment", backref="user", lazy=True)
    t2_responses = db.relationship('ResponseT2', 
                                        foreign_keys=[ResponseT2.user_id], 
                                        backref=db.backref('responding_student', lazy='joined'),
                                        lazy='dynamic', 
                                        # delete orphan - so if a user is deleted, 
                                        # it deletes their orphaned relationships too
                                        cascade='all, delete-orphan', 
                                        )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.is_admin:
                self.role = Role.query.filter_by(name="Lecturer").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # def has_answered(question, assessment):
    #     if question.q_t2_id is None: 
    #         return False 
    #     return self.t2_responses.filter_by(question_id)

    def __repr__(self):
        return f"User: {self.name}"


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'Student': [Permission.ANSWER_ASSESSMENT], 
            'Lecturer': [Permission.WRITE_ASSESSMENT, Permission.ADMIN], 
            'Admin': [Permission.ADMIN]
        }
        default_role = "Student"
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f"Role: {self.name}"


class Permission:
    WRITE_ASSESSMENT = 1
    ANSWER_ASSESSMENT = 2
    ADMIN = 4


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
