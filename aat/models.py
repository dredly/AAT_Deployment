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


class Course(db.Model):
    __tablename__ = "Course"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(
        db.String(30), unique=True, nullable=False, default="MSc. Computing"
    )
    modules = db.relationship("Module", backref="course")

    def __repr__(self):
        return self.title

    def get_count_of_modules(self):
        return len(self.modules)

    def get_count_of_all_correct_and_incorrect_responses(
        self, user_id, summative_only=None, formative_only=None
    ):
        count = {"correct": 0, "incorrect": 0}
        for response in [
            ResponseT1.query.filter_by(user_id=user_id).all(),
            ResponseT1.query.filter_by(user_id=user_id).all(),
        ]:
            for r in response:
                if (
                    (not summative_only and not formative_only)
                    or (summative_only and r.assessment.is_summative)
                    or (formative_only and not r.assessment.is_summative)
                ):
                    if r.is_correct:
                        count["correct"] += 1
                    else:
                        count["incorrect"] += 1
        return count

    def get_status_counter(self, user_id):
        return Counter([m.get_status(user_id) for m in self.modules])

    def get_status(self, user_id):
        counter_of_module_status = self.get_status_counter(user_id)
        count_of_modules = self.get_count_of_modules()
        if counter_of_module_status.get("pass") == count_of_modules:
            return "pass"
        if counter_of_module_status.get("fail") == count_of_modules:
            return "fail"
        if counter_of_module_status.get("in progress", 0) > 0:
            return "in progress"
        return "unattempted"

    def get_modules(self):
        """
        Returns list of all assessments attached to module
        Can be filtered summative/formative
        """
        return self.modules

    def get_dict_of_tags_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):

        list_of_module_values = [
            m.get_dict_of_tags_and_answers(user_id, summative_only, formative_only)
            for m in self.modules
        ]

        output_dict = {}
        for item in list_of_module_values:
            for key, value in item.items():
                output_dict.setdefault(key, {"correct": 0, "incorrect": 0})
                output_dict[key]["correct"] += value["correct"]
                output_dict[key]["incorrect"] += value["incorrect"]

        return output_dict

    def get_dict_of_difficulty_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):
        output_dict = {
            1: {"correct": 0, "incorrect": 0},
            2: {"correct": 0, "incorrect": 0},
            3: {"correct": 0, "incorrect": 0},
        }

        for m in self.modules:
            for key, value in output_dict.items():
                for v in value:
                    output_dict[key][v] += m.get_dict_of_difficulty_and_answers(
                        user_id, summative_only, formative_only
                    )[key][v]

        return output_dict

    def get_dict_of_type_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):
        output_dict = {
            1: {"correct": 0, "incorrect": 0},
            2: {"correct": 0, "incorrect": 0},
        }

        for m in self.modules:
            for key, value in output_dict.items():
                for v in value:
                    output_dict[key][v] += m.get_dict_of_type_and_answers(
                        user_id, summative_only, formative_only
                    )[key][v]

        return output_dict


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

    def get_type(self):
        return 1

    def get_feedback(self):
        return (
            self.question.feedback_if_correct
            if self.is_correct
            else self.question.feedback_if_wrong
        )

    def get_feedforward(self):
        return (
            self.question.feedforward_if_correct
            if self.is_correct
            else self.question.feedforward_if_wrong
        )

    def get_status(self):
        return "pass" if self.is_correct else "fail"

    def get_answer_given(self):
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

    def get_type(self):
        return 2

    def get_feedback(self):
        return (
            self.question.feedback_if_correct
            if self.is_correct
            else self.question.feedback_if_wrong
        )

    def get_feedforward(self):
        return (
            self.question.feedforward_if_correct
            if self.is_correct
            else self.question.feedforward_if_wrong
        )

    def get_status(self):
        return "pass" if self.is_correct else "fail"

    def get_answer_given(self):
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

    def get_questions(self):
        return [
            q for question in [self.question_t1, self.question_t2] for q in question
        ]

    def get_responses(self, user_id=None, attempt_number=None):
        if user_id and attempt_number:
            return [
                r
                for response in [self.responses_t1, self.responses_t2]
                for r in response
                if r.user_id == user_id and r.attempt_number == attempt_number
            ]

        if user_id:
            return [
                r
                for response in [self.responses_t1, self.responses_t2]
                for r in response
                if r.user_id == user_id
            ]

        return [
            r for response in [self.responses_t1, self.responses_t2] for r in response
        ]

    def get_attempt_limit(self):
        return 3 if self.is_summative else None

    def get_can_user_take_assessment(self, user_id):
        return (
            True
            if not self.is_summative
            else self.get_count_of_attempts_made(user_id) < self.get_attempt_limit()
        )

    def get_total_marks_possible(self):
        """
        Returns the total number of marks an assessment is worth
        """
        return sum(
            q.num_of_marks
            for question in [self.question_t1, self.question_t2]
            for q in question
        )

    def get_count_of_attempts_made(self, user_id):
        return max(self.get_marks_for_user_and_assessment(user_id).keys())

    def get_list_of_attempts_made(self, user_id):
        return self.get_marks_for_user_and_assessment(user_id).keys()

    def get_average_difficulty(self, actual=False):
        """
        Returns average difficulty (string)
        """
        sum_val = sum(
            [
                q.difficulty
                for question in [self.question_t1, self.question_t2]
                for q in question
            ]
        )

        len_val = len([self.question_t1, self.question_t2])

        if actual:
            return sum_val / len_val
        else:
            return round(sum_val / len_val)

    def question_filter(self, question, summative_only, formative_only):
        if summative_only:
            return [q for q in question if q.assessment.is_summative]
        if formative_only:
            return [q for q in question if not q.assessment.is_summative]
        return question

    def get_dict_of_questions_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
        hsa_only=None,
    ):
        output_dict = {
            "count": 0,
            "correct": 0,
            "incorrect": 0,
        }
        for question in [self.question_t1, self.question_t2]:
            question = self.question_filter(question, summative_only, formative_only)
            for q in question:
                if hsa_only:
                    #
                    check = q.get_was_user_right(user_id)
                    if check is None:
                        continue
                    if check is True:
                        output_dict["correct"] += 1
                        output_dict["count"] += 1
                    if check is False:
                        output_dict["incorrect"] += 1
                        output_dict["count"] += 1

                else:
                    # Get list of attempts
                    for specific_attempt in range(
                        self.get_count_of_attempts_made(user_id)
                    ):
                        check = q.get_was_user_right(user_id, specific_attempt + 1)
                        if check is None:
                            continue
                        if check is True:
                            output_dict["correct"] += 1
                            output_dict["count"] += 1

                        if check is False:
                            output_dict["incorrect"] += 1
                            output_dict["count"] += 1
        return output_dict

    def get_dict_of_tags_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
        hsa_only=None,
    ):
        """
        Returns tags and times the correct answer was given for the highest scoring attempt
        Opt: takes in specific attempt - if not then uses highest scoring attempt
        """
        output_dict = {}
        for question in [self.question_t1, self.question_t2]:
            question = self.question_filter(question, summative_only, formative_only)
            for q in question:
                output_dict.setdefault(q.tag, {"correct": 0, "incorrect": 0})
                if hsa_only:
                    #
                    check = q.get_was_user_right(user_id)
                    if check is None:
                        continue
                    if check is True:
                        output_dict[q.tag]["correct"] += 1
                    if check is False:
                        output_dict[q.tag]["incorrect"] += 1
                else:
                    # Get list of attempts
                    for specific_attempt in range(
                        self.get_count_of_attempts_made(user_id)
                    ):
                        check = q.get_was_user_right(user_id, specific_attempt + 1)
                        if check is None:
                            continue
                        if check is True:
                            output_dict[q.tag]["correct"] += 1
                        if check is False:
                            output_dict[q.tag]["incorrect"] += 1
        return output_dict

    def get_dict_of_difficulty_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
        hsa_only=None,
    ):
        """
        Returns difficulty and times the correct answer was given for the highest scoring attempt
        Opt: takes in specific attempt - if not then uses highest scoring attempt
        """
        output_dict = {
            1: {"correct": 0, "incorrect": 0},
            2: {"correct": 0, "incorrect": 0},
            3: {"correct": 0, "incorrect": 0},
        }
        for question in [self.question_t1, self.question_t2]:
            question = self.question_filter(question, summative_only, formative_only)
            for q in question:
                if hsa_only:
                    check = q.get_was_user_right(user_id)
                    if check is None:
                        continue
                    if check is True:
                        output_dict[q.difficulty]["correct"] += 1
                    if check is False:
                        output_dict[q.difficulty]["incorrect"] += 1
                else:
                    # Get list of attempts
                    for specific_attempt in range(
                        self.get_count_of_attempts_made(user_id)
                    ):
                        check = q.get_was_user_right(user_id, specific_attempt + 1)
                        if check is None:
                            continue
                        if check is True:
                            output_dict[q.difficulty]["correct"] += 1
                        if check is False:
                            output_dict[q.difficulty]["incorrect"] += 1
        return output_dict

    def get_dict_of_type_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
        hsa_only=None,
    ):
        """
        Returns type and times the correct answer was given for the highest scoring attempt
        Opt: takes in specific attempt - if not then uses highest scoring attempt
        """
        output_dict = {
            1: {"correct": 0, "incorrect": 0},
            2: {"correct": 0, "incorrect": 0},
        }
        for question in [self.question_t1, self.question_t2]:
            question = self.question_filter(question, summative_only, formative_only)
            for q in question:
                if hsa_only:
                    check = q.get_was_user_right(user_id)
                    if check is None:
                        continue
                    if check is True:
                        output_dict[q.get_type()]["correct"] += 1
                    if check is False:
                        output_dict[q.get_type()]["incorrect"] += 1
                else:
                    # Get list of attempts
                    for specific_attempt in range(
                        self.get_count_of_attempts_made(user_id)
                    ):
                        check = q.get_was_user_right(user_id, specific_attempt + 1)
                        if check is None:
                            continue
                        if check is True:
                            output_dict[q.get_type()]["correct"] += 1
                        if check is False:
                            output_dict[q.get_type()]["incorrect"] += 1
        return output_dict

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

    def get_status_of_attempt(self, user_id, attempt_number):
        return (
            "pass"
            if (
                self.get_marks_for_user_and_assessment(user_id)[attempt_number]
                / self.get_total_marks_possible()
            )
            >= 0.5
            else "fail"
        )

    def get_credits(self, user_id):
        if self.get_status(user_id) == "pass":
            return self.num_of_credits
        return 0

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

    def get_all_tags(self):
        return [tag for tag in self.name]


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

    def get_question_id(self):
        return self.q_t1_id

    def get_type(self):
        return 1

    def get_responses_from_user(self, user_id, attempt_number=None):
        if not attempt_number:
            return [r for r in self.responses if r.user_id == user_id]
        else:
            return [
                r
                for r in self.responses
                if r.user_id == user_id and r.attempt_number == attempt_number
            ]

    def get_weighted_marks(self):
        """
        Looks at all marks in attached assessment
        Calculates the relative weight of this question's num_of_marks (%)
        """
        try:
            return self.num_of_marks / self.assessment.get_total_marks_possible()
        except:
            return None

    def get_was_user_right(self, user_id, attempt_number=None):
        """
        Looks at the user and their highest scoring attempt
        Checks if the user got the correct answer
        """
        if attempt_number is None:
            if not self.assessment.get_highest_scoring_attempt_and_mark(user_id):
                return False
            attempt_number = self.assessment.get_highest_scoring_attempt_and_mark(
                user_id
            ).get("highest_scoring_attempt")
            if not attempt_number:
                return False
        for r in self.responses:
            if r.user_id == user_id and r.attempt_number == attempt_number:
                return r.is_correct
        return None


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

    def get_question_id(self):
        return self.q_t2_id

    def get_type(self):
        return 2

    def get_responses_from_user(self, user_id, attempt_number=None):
        if not attempt_number:
            return [r for r in self.responses if r.user_id == user_id]
        else:
            return [
                r
                for r in self.responses
                if r.user_id == user_id and r.attempt_number == attempt_number
            ]

    def get_weighted_marks(self):
        """
        Looks at all marks in attached assessment
        Calculates the relative weight of this question's num_of_marks (%)
        """
        try:
            return self.num_of_marks / self.assessment.get_total_marks_possible()
        except:
            return None

    def get_was_user_right(self, user_id, attempt_number=None):
        """
        Looks at the user and their highest scoring attempt
        Checks if the user got the correct answer
        """
        if attempt_number is None:
            if not self.assessment.get_highest_scoring_attempt_and_mark(user_id):
                return False
            attempt_number = self.assessment.get_highest_scoring_attempt_and_mark(
                user_id
            ).get("highest_scoring_attempt")
            if not attempt_number:
                return False
        for r in self.responses:
            if r.user_id == user_id and r.attempt_number == attempt_number:
                return r.is_correct
        return None


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
    # --- Foreign keys ---
    course_id = db.Column(db.Integer, db.ForeignKey("Course.id"), default=1)
    # --- Relationships ---
    assessments = db.relationship("Assessment", backref="module", lazy=True)

    def __repr__(self):
        return self.title

    def get_total_assessment_credits(self):
        """
        Adds up total_credits
        """
        return sum([a.num_of_credits for a in self.assessments])

    def get_total_marks_possible(self, summative_only=False, formative_only=False):
        if summative_only:
            return sum(
                [
                    a.get_total_marks_possible()
                    for a in self.assessments
                    if a.is_summative
                ]
            )
        if formative_only:
            return sum(
                [
                    a.get_total_marks_possible()
                    for a in self.assessments
                    if not a.is_summative
                ]
            )
        return sum([a.get_total_marks_possible() for a in self.assessments])

    def get_total_marks_earned(
        self, user_id, summative_only=False, formative_only=False
    ):
        if summative_only:
            return sum(
                [
                    a.get_highest_scoring_attempt_and_mark(user_id)["highest_score"]
                    for a in self.assessments
                    if a.get_status(user_id) != "unattempted" and a.is_summative
                ]
            )
        if formative_only:
            return sum(
                [
                    a.get_highest_scoring_attempt_and_mark(user_id)["highest_score"]
                    for a in self.assessments
                    if a.get_status(user_id) != "unattempted" and not a.is_summative
                ]
            )
        return sum(
            [
                a.get_highest_scoring_attempt_and_mark(user_id)["highest_score"]
                for a in self.assessments
                if a.get_status(user_id) != "unattempted"
            ]
        )

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

    def get_assessments(self, summative_only=False, formative_only=False):
        """
        Returns list of all assessments attached to module
        Can be filtered summative/formative
        """
        if summative_only:
            return [a for a in self.assessments if a.is_summative]
        if formative_only:
            return [a for a in self.assessments if not a.is_summative]
        return self.assessments

    def get_count_of_taken_assessments(
        self, user_id, summative_only=False, formative_only=False
    ):
        if summative_only:
            return len(
                [
                    a
                    for a in self.get_assessments()
                    if a.get_status(user_id) in ["pass", "fail"] and a.is_summative
                ]
            )
        return len(
            [
                a
                for a in self.get_assessments()
                if a.get_status(user_id) in ["pass", "fail"]
            ]
        )

    def get_dict_of_tags_and_assessments(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):
        """
        Returns {tags : [assessments]}
        """
        output = {}
        tags_used = self.get_dict_of_tags_and_answers(user_id).keys()
        for tag in tags_used:
            output[tag] = []
            for a in self.get_assessments(
                summative_only=summative_only, formative_only=formative_only
            ):
                if tag in a.get_dict_of_tags_and_answers(user_id).keys():
                    output[tag].append(a)
        return output

    def get_dict_of_tags_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):
        # Summative ONLY
        output = {}
        for a in self.get_assessments(summative_only, formative_only):
            input_dict = a.get_dict_of_tags_and_answers(user_id)
            for key, value in input_dict.items():
                if key not in output:
                    output[key] = value
                else:
                    for v, val in value.items():
                        output[key][v] += val
        return output

    def get_dict_of_difficulty_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):
        output_dict = {
            1: {"correct": 0, "incorrect": 0},
            2: {"correct": 0, "incorrect": 0},
            3: {"correct": 0, "incorrect": 0},
        }

        for a in self.get_assessments(summative_only, formative_only):
            for key, value in output_dict.items():
                for v in value:
                    output_dict[key][v] += a.get_dict_of_difficulty_and_answers(
                        user_id
                    )[key][v]

        return output_dict

    def get_dict_of_type_and_answers(
        self,
        user_id,
        summative_only=None,
        formative_only=None,
    ):
        output_dict = {
            1: {"correct": 0, "incorrect": 0},
            2: {"correct": 0, "incorrect": 0},
        }

        for a in self.get_assessments(summative_only, formative_only):
            for key, value in output_dict.items():
                for v in value:
                    output_dict[key][v] += a.get_dict_of_type_and_answers(user_id)[key][
                        v
                    ]

        return output_dict

    def get_average_difficulty(self):
        return round(
            sum(
                [a.get_average_difficulty() for a in self.assessments if a.is_summative]
            )
            / len([a for a in self.assessments if a.is_summative])
        )

    def get_count_of_assessments(
        self,
        summative_only=False,
        formative_only=False,
        status_counter=False,
        user_id=None,
    ):
        """
        Returns count of assessments
        Has filters for summative and formative
        Also allows you to ask if passed (requires user_id)
        """
        if summative_only:
            if status_counter:
                return Counter(
                    [a.get_status(user_id) for a in self.assessments if a.is_summative]
                )
            return len([a for a in self.assessments if a.is_summative])
        if formative_only:
            if status_counter:
                return Counter([a.get_status(user_id) for a in self.assessments])
            return len(
                [a for a in self.assessments if not a.is_summative if a.is_summative]
            )

        return len(self.assessments)


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
        for response in t2_responses:
            new_key = f"t2_{response.t2_question_id}"
            if new_key in attempts:
                attempts[new_key] = attempts[new_key] + 1
            else:
                attempts[new_key] = 1
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
