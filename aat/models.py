from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask_login import LoginManager
from collections import Counter

# First trying to get it working without model inheritance

db = SQLAlchemy()
login_manager = LoginManager()

# Format for model: primary key, then all foreign keys, then all other columns, then all relationships


class Challenge(db.Model):
    __tablename__ = "challenges"
    challenge_id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    to_user = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Text, default="Pending")
    difficulty = db.Column(db.Integer, default=0)
    number_of_questions = db.Column(db.Integer, default=3)
    challenge_questions_id = db.relationship(
        "ChallengeQuestions", backref="challenges", lazy=True
    )


class ChallengeQuestions(db.Model):
    __tablename__ = "challenge_questions"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.challenge_id"), nullable=False
    )
    question_id = db.Column(db.Integer, nullable=False)


class ChallengesTaken(db.Model):
    __tablename__ = "challenges_taken"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.challenge_id"), nullable=False
    )


class Friends(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)


class Tier(db.Model):
    __tablename__ = "tiers"
    tier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    level = db.Column(db.Integer, nullable=False)


class Badge(db.Model):
    __tablename__ = "badges"
    badge_id = db.Column(db.Integer, primary_key=True)
    # --- Relationships ---
    awarded_badge = db.relationship("Awarded_Badge", backref="badge", lazy=True)
    # --- Other Columns ---
    name = db.Column(db.String(20))
    description = db.Column(db.Text)

    def __repr__(self):
        return self.name


class Achievement(db.Model):
    __tablename__ = "achievements"
    achievement_id = db.Column(db.Integer, primary_key=True)
    # --- Relationships ---
    awarded_achievement = db.relationship(
        "Awarded_Achievement", backref="achievement", lazy=True
    )
    # --- Other Columns ---
    name = db.Column(db.String(20))
    description = db.Column(db.Text)

    def __repr__(self):
        return self.name


class Awarded_Badge(db.Model):
    __tablename__ = "awarded_badges"
    id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # --- Other Columns ---
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.badge_id"), nullable=False)


class Awarded_Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # --- Other Columns ---
    achievement_id = db.Column(
        db.Integer, db.ForeignKey("achievements.achievement_id"), nullable=False
    )


class ResponseT1(db.Model):
    __tablename__ = "t1_responses"
    attempt_number = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("Assessment.assessment_id"), primary_key=True
    )
    t1_question_id = db.Column(
        db.Integer, db.ForeignKey("QuestionT1.q_t1_id"), primary_key=True
    )
    selected_option = db.Column(
        db.Integer, db.ForeignKey("Option.option_id"), primary_key=True
    )
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return self.chosen_option.option_text


class ResponseT2(db.Model):
    """
    Response models adapted from code used to represent 'Followers'
    Flask Web Development, 2nd Edition by Miguel Grinberg
    https://learning.oreilly.com/library/view/flask-web-development/9781491991725/ch13.html
    Particular sections used include:
    ------ Chapter 12: Followers
    """

    __tablename__ = "t2_responses"
    attempt_number = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("Assessment.assessment_id"), primary_key=True
    )
    t2_question_id = db.Column(
        db.Integer, db.ForeignKey("QuestionT2.q_t2_id"), primary_key=True
    )
    response_content = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return self.response_content


class Assessment(db.Model):
    __tablename__ = "Assessment"
    assessment_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys --- CONTAINS PLACEHOLDERS
    module_id = db.Column(db.Integer, db.ForeignKey("Module.module_id"))
    lecturer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # --- Other Columns ---
    title = db.Column(db.String(120), nullable=False, unique=True)
    due_date = db.Column(db.DateTime())
    time_limit = db.Column(db.Integer)  # Time limit in seconds
    num_of_credits = db.Column(db.Integer, nullable=True, default=0)
    is_summative = db.Column(
        db.Boolean, nullable=True, default=False, server_default="False"
    )
    # --- Relationships --- TODO: add more as tables are added to the db
    question_t1 = db.relationship("QuestionT1", backref="assessment", lazy=True)
    question_t2 = db.relationship("QuestionT2", backref="assessment", lazy=True)
    responses_t1 = db.relationship(
        "ResponseT1",
        foreign_keys=[ResponseT1.assessment_id],
        backref=db.backref("assessment", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    responses_t2 = db.relationship(
        "ResponseT2",
        foreign_keys=[ResponseT2.assessment_id],
        backref=db.backref("assessment", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return self.title

    def get_attempt_limit(self):
        return 3 if self.is_summative else None

    def get_total_marks_possible(self):
        """
        Returns the total number of marks an assessment is worth
        """
        return sum(
            q.num_of_marks
            for question in [self.question_t1, self.question_t2]
            for q in question
        )

    def get_marks_for_user_and_assessment(self, user_id):
        """
        Returns dictionary of:
        - attempt id (int)
        - total marks received for that attempt
        """
        dict_of_attempt_and_marks = {}
        for res in [self.responses_t1, self.responses_t2]:
            for r in res:
                if r.user_id == user_id:
                    marks_awarded = r.question.num_of_marks if r.is_correct else 0
                    dict_of_attempt_and_marks[r.attempt_number] = (
                        dict_of_attempt_and_marks.setdefault(r.attempt_number, 0)
                        + marks_awarded
                    )
        return dict_of_attempt_and_marks

    def get_highest_scoring_attempt_and_mark(self, user_id):
        """
        Returns a dictionary of:
        - highest_scoring_attempt (int)
        - highest_score (int)
        """
        dict_of_attempt_and_marks = self.get_marks_for_user_and_assessment(user_id)
        if not dict_of_attempt_and_marks:
            return None
        # https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        highest_scoring_attempt = max(
            dict_of_attempt_and_marks,
            key=dict_of_attempt_and_marks.get,
        )
        return {
            "highest_scoring_attempt": highest_scoring_attempt,
            "highest_score": dict_of_attempt_and_marks[highest_scoring_attempt],
        }

    def get_status(self, user_id):
        """
        Returns status (string) based on a user's answers:
        -- "pass": total_marks >= 50%
        -- "fail": total_marks < 50%
        -- "unattempted": student submitted any attempts

        """
        highest_scoring_attempt_and_mark = self.get_highest_scoring_attempt_and_mark(
            user_id
        )
        if not highest_scoring_attempt_and_mark:
            return "unattempted"
        if (
            highest_scoring_attempt_and_mark["highest_score"]
            / self.get_total_marks_possible()
            >= 0.5
        ):
            return "pass"
        return "fail"

    def get_weighted_perc_factor(self):
        """
        Works out total weighted perc for this assessment
        Is not calculated if user hasn't attempted or if it's a formative assessment
        """
        return self.num_of_credits / self.module.get_total_assessment_credits()

    def get_total_weighted_marks_as_perc(self, user_id):
        weighted_factor = self.get_weighted_perc_factor()
        # Get total marks earned
        total_marks_earned = self.get_highest_scoring_attempt_and_mark(user_id=user_id)[
            "highest_score"
        ]
        total_marks_as_percentage = total_marks_earned / self.get_total_marks_possible()
        return weighted_factor * total_marks_as_percentage


class Tag(db.Model):
    __tablename__ = "Tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    # --- Relationships ---
    question_t1 = db.relationship("QuestionT1", backref="tag", lazy=True)
    question_t2 = db.relationship("QuestionT2", backref="tag", lazy=True)

    def __repr__(self):
        return self.name


class QuestionT1(db.Model):
    __tablename__ = "QuestionT1"
    q_t1_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    assessment_id = db.Column(db.Integer, db.ForeignKey("Assessment.assessment_id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("Tag.id"))
    # --- Other Columns ---
    num_of_marks = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    feedback_if_correct = db.Column(db.Text, nullable=False)
    feedback_if_wrong = db.Column(db.Text, nullable=False)
    feedforward_if_correct = db.Column(db.Text, nullable=False)
    feedforward_if_wrong = db.Column(db.Text, nullable=False)
    # --- Relationships ---
    option = db.relationship(
        "Option", backref="questiont1", lazy=True, cascade="all, delete-orphan"
    )
    responses = db.relationship(
        "ResponseT1",
        foreign_keys=[ResponseT1.t1_question_id],
        backref=db.backref("question", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return self.question_text

    def get_weighted_marks(self):
        """
        Looks at all marks in attached assessment
        Calculates the relative weight of this question's num_of_marks (%)
        """
        try:
            return self.num_of_marks / self.assessment.get_total_marks_possible()
        except:
            return None

    def get_was_user_right(self, user_id, attempt_number):
        """
        Looks at the user and the attempt
        Checks if the user got the correct answer
        """
        for r in self.responses:
            if r.user_id == user_id and r.attempt_number == attempt_number:
                return r.is_correct


class QuestionT2(db.Model):
    __tablename__ = "QuestionT2"
    q_t2_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    assessment_id = db.Column(db.Integer, db.ForeignKey("Assessment.assessment_id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("Tag.id"))
    # --- Other Columns ---
    num_of_marks = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    feedback_if_correct = db.Column(db.Text, nullable=False)
    feedback_if_wrong = db.Column(db.Text, nullable=False)
    feedforward_if_correct = db.Column(db.Text, nullable=False)
    feedforward_if_wrong = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    responses = db.relationship(
        "ResponseT2",
        foreign_keys=[ResponseT2.t2_question_id],
        backref=db.backref("question", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return self.question_text

    def get_weighted_marks(self):
        """
        Looks at all marks in attached assessment
        Calculates the relative weight of this question's num_of_marks (%)
        """
        try:
            return self.num_of_marks / self.assessment.get_total_marks_possible()
        except:
            return None

    def get_was_user_right(self, user_id, attempt_number):
        """
        Looks at the user and the attempt
        Checks if the user got the correct answer
        """
        for r in self.responses:
            if r.user_id == user_id and r.attempt_number == attempt_number:
                return r.is_correct


class Option(db.Model):
    __tablename__ = "Option"
    option_id = db.Column(db.Integer, primary_key=True)
    # --- Foreign Keys ---
    q_t1_id = db.Column(db.Integer, db.ForeignKey("QuestionT1.q_t1_id"), nullable=False)
    # ---- Other Columns ---
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    # ---- Relationships ----
    responses_selected_in = db.relationship(
        "ResponseT1",
        foreign_keys=[ResponseT1.selected_option],
        backref=db.backref("chosen_option", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return self.option_text


class Module(db.Model):
    __tablename__ = "Module"
    module_id = db.Column(db.Integer, primary_key=True)
    # --- Other Columns ---
    title = db.Column(db.String(120), unique=True, nullable=False)
    total_credits = db.Column(
        db.Integer, nullable=False
    )  # DO NOT USE - use get_total_assessment_credits() instead
    # --- Relationships ---
    assessments = db.relationship("Assessment", backref="module", lazy=True)

    def __repr__(self):
        return self.title

    def get_total_assessment_credits(self):
        """
        Adds up total_credits
        """
        return sum([a.num_of_credits for a in self.assessments])

    def get_total_weighted_marks_as_perc(self, user_id):
        """
        Returns weighted percentage for a user's performance based on summative assessments
        """
        return sum(
            [
                a.get_total_weighted_marks_as_perc(user_id)
                for a in self.assessments
                if a.get_status(user_id) != "unattempted" and a.is_summative
            ]
        )

    def get_status(self, user_id):
        """
        Returns status (string) based on a user's answers:
        -- pass: total_weighted_percentage >= 50%
        -- fail: total_weighted_percentage < 50% AND all assessments attempted
        -- in progress: total_weighted_percentage < 50% AND all assessments NOT attempted
        -- unattempted: no assessments have been attempted
        """
        # Unattempted:
        counter_of_status = Counter([a.get_status(user_id) for a in self.assessments])
        if counter_of_status["unattempted"] == len(self.assessments):
            return "unattempted"
        # Pass:
        if self.get_total_weighted_marks_as_perc(user_id) >= 0.5:
            return "pass"

        # Fail
        if counter_of_status["unattempted"] == 0:
            return "fail"

        # Unattempted
        return "in progress"


class User(UserMixin, db.Model):
    """
    User and Role Models, and their included methods, adapted from
    Flask Web Development, 2nd Edition by Miguel Grinberg
    https://learning.oreilly.com/library/view/flask-web-development/9781491991725/ch13.html
    Particular sections used include:
    ------ Chapter 8: User Authentication
    ------ Chapter 9: User Roles
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128))
    tier = db.Column(db.String(10), default="Bronze")
    # If is_admin is set to True, any given role will be overridden to give max access
    # (i.e. the User will be given a lecturer role)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    email = db.Column(db.String(64), nullable=True, default="jacksonr16@cardiff.ac.uk")
    # --- Relationships ---
    friends = db.relationship("Friends", backref="user", lazy=True)
    assessments = db.relationship("Assessment", backref="user", lazy=True)
    awarded_badge = db.relationship("Awarded_Badge", backref="user", lazy=True)
    awarded_achievement = db.relationship(
        "Awarded_Achievement", backref="user", lazy=True
    )
    challenge_from = db.relationship(
        "Challenge", foreign_keys="Challenge.from_user", backref="users", lazy="dynamic"
    )
    t1_responses = db.relationship(
        "ResponseT1",
        foreign_keys="ResponseT1.user_id",
        backref=db.backref("responding_student", lazy="joined"),
        lazy="dynamic",
        # delete orphan - so if a user is deleted,
        # it deletes their orphaned relationships too
        cascade="all, delete-orphan",
    )
    t2_responses = db.relationship(
        "ResponseT2",
        foreign_keys="ResponseT2.user_id",
        backref=db.backref("responding_student", lazy="joined"),
        lazy="dynamic",
        # delete orphan - so if a user is deleted,
        # it deletes their orphaned relationships too
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        # If is_admin is set to True, any given role will be overridden to give max access
        # (i.e. the User will be given a lecturer role)
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

    def has_taken(self, assessment):
        if assessment.assessment_id is None:
            return False

        type_1s = self.t1_responses.filter_by(
            assessment_id=assessment.assessment_id
        ).all()
        type_2s = self.t2_responses.filter_by(
            assessment_id=assessment.assessment_id
        ).all()
        if len(type_1s) <= 0 and len(type_2s) <= 0:
            return False
        else:
            return True

    def current_attempts(self, assessment):
        if not self.has_taken(assessment):
            return 0
        t1_responses = self.t1_responses.filter_by(
            assessment_id=assessment.assessment_id
        ).all()
        t2_responses = self.t2_responses.filter_by(
            assessment_id=assessment.assessment_id
        ).all()
        attempts = dict()
        for response in t1_responses:
            new_key = f"t1_{response.t1_question_id}"
            if new_key in attempts:
                attempts[new_key] = attempts[new_key] + 1
            else:
                attempts[new_key] = 1
                # print(response)
        for response in t2_responses:
            new_key = f"t2_{response.t2_question_id}"
            if new_key in attempts:
                attempts[new_key] = attempts[new_key] + 1
            else:
                attempts[new_key] = 1
            # print(response)
        highest_number_of_responses = max(attempts, key=attempts.get)
        taken_attempts = attempts[highest_number_of_responses]
        return taken_attempts

    def has_answered(self, type, question, assessment, attempt):
        if assessment.assessment_id is None:
            return False
        if type == 1:  # q_t1_id
            if question.q_t1_id is None:
                return False
            return (
                self.t1_responses.filter_by(t1_question_id=question.q_t1_id)
                .filter_by(assessment_id=assessment.assessment_id)
                .filter_by(attempt_number=attempt)
                .first()
                is not None
            )
        elif type == 2:
            if question.q_t2_id is None:
                return False
            if assessment.assessment_id is None:
                return False
            return (
                self.t2_responses.filter_by(t2_question_id=question.q_t2_id)
                .filter_by(assessment_id=assessment.assessment_id)
                .filter_by(attempt_number=attempt)
                .first()
                is not None
            )

    def remove_answer(self, type, question, assessment, attempt):
        if type == 1:
            response = (
                self.t1_responses.filter_by(t1_question_id=question.q_t1_id)
                .filter_by(assessment_id=assessment.assessment_id)
                .filter_by(attempt_number=attempt)
                .first()
            )
        elif type == 2:
            response = (
                self.t2_responses.filter_by(t2_question_id=question.q_t2_id)
                .filter_by(assessment_id=assessment.assessment_id)
                .filter_by(attempt_number=attempt)
                .first()
            )
        if response:
            db.session.delete(response)

    def get_course_status(self):
        """
        -- pass: all modules have "pass" status
        -- fail: all modules have "fail" status
        -- in progress: any modules have "in progress" status
        -- unattempted: all modules have "unattempted" status
        """
        module_query = Module.query.all()
        # Unattempted:
        counter_of_modules = Counter(m.get_status(self.id) for m in module_query)
        if counter_of_modules["unattempted"] == len(module_query):
            return "unattempted"
        # Pass:
        if counter_of_modules["pass"] == len(module_query):
            return "pass"

        # Fail
        if counter_of_modules["fail"] == len(module_query):
            return "fail"

        # Unattempted
        return "in progress"

    def __repr__(self):
        return f"User: {self.name}"


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Role(db.Model):
    """
    User and Role Models, and their included methods, adapted from
    Flask Web Development, 2nd Edition by Miguel Grinberg
    https://learning.oreilly.com/library/view/flask-web-development/9781491991725/ch13.html
    Particular sections used include:
    ------ Chapter 8: User Authentication
    ------ Chapter 9: User Roles
    """

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
            "Student": [Permission.ANSWER_ASSESSMENT],
            "Lecturer": [Permission.WRITE_ASSESSMENT, Permission.ADMIN],
            "Admin": [Permission.ADMIN],
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
