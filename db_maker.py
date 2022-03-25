from aat import db
from aat import Role
from aat import app

from aat.models import *


with app.app_context():
    db.drop_all()
    db.create_all()
    Role.insert_roles()

    ###########
    # MODULES #
    ###########
    db.session.add_all(
        [
            Module(  # 1
                title="Databases and Modelling",
                total_credits=120,
            ),
            Module(  # 2
                title="Advanced BennieScript",
                total_credits=30,
            ),
        ]
    )

    ###############
    # ASSESSMENTS #
    ###############
    db.session.add_all(
        [
            Assessment(  # 1
                module_id=1,
                lecturer_id=1,
                title="Git Basics",
                due_date=None,
                time_limit=60 * 60 * 30,
                num_of_credits=12,
                is_summative=True,
            ),
            Assessment(  # 2
                module_id=1,
                lecturer_id=2,
                title="Advanced Git",
                due_date=None,
                time_limit=60 * 60 * 45,
                num_of_credits=10,
                is_summative=True,
            ),
            Assessment(  # 3
                module_id=1,
                lecturer_id=3,
                title="DOM Manipulation in JS",
                due_date=None,
                time_limit=60 * 60 * 20,
                num_of_credits=0,
                is_summative=False,
            ),
            Assessment(  # 4
                module_id=2,
                lecturer_id=1,
                title="Woof",
                due_date=None,
                num_of_credits=10,
                is_summative=True,
            ),
        ]
    )

    #####################
    # QUESTIONS: TYPE 1 #
    #####################
    db.session.add_all(
        [
            QuestionT1(  # 1
                assessment_id=1,
                num_of_marks=2,
                question_text="Which command do use use to view a particular commit?",
                difficulty=1,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT1(  # 2
                assessment_id=2,
                num_of_marks=5,
                question_text="What does git rebase do?",
                difficulty=3,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT1(  # 3
                assessment_id=2,
                num_of_marks=5,
                question_text="What does git stash do?",
                difficulty=2,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
        ]
    )

    ###########
    # OPTIONS #
    ###########
    db.session.add_all(
        [
            Option(q_t1_id=1, option_text="checkout", is_correct=True),  # 1
            Option(q_t1_id=1, option_text="reset"),  # 2
            Option(q_t1_id=1, option_text="commit"),  # 3
            Option(q_t1_id=2, option_text="wrong answer"),  # 4
            Option(q_t1_id=2, option_text="right answer", is_correct=True),  # 5
            Option(q_t1_id=3, option_text="wrong answer"),  # 6
            Option(q_t1_id=3, option_text="right answer", is_correct=True),  # 7
            Option(q_t1_id=3, option_text="another wrong answer"),  # 8
        ]
    )

    #####################
    # QUESTIONS: TYPE 2 #
    #####################
    db.session.add_all(
        [
            QuestionT2(  # 1
                assessment_id=1,
                num_of_marks=5,
                question_text="What flag do you use to add a commit message?",
                correct_answer="-m",
                difficulty=1,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT2(  # 2
                assessment_id=1,
                num_of_marks=10,
                question_text="which command is used to upload your commits to a remote repository?",
                correct_answer="push",
                difficulty=1,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT2(  # 3
                assessment_id=3,
                num_of_marks=10,
                question_text="Which symbol is used to select by class using document.querySelector()?",
                correct_answer=".",
                difficulty=2,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT2(  # 4
                assessment_id=4,
                num_of_marks=5,
                question_text="Bark?",
                correct_answer="Bark!",
                difficulty=3,
                feedback_if_correct="WOOF!",
                feedback_if_wrong="GRRRRRRRRRR",
            ),
        ]
    )

    #########
    # USERS #
    #########
    db.session.add_all(
        [
            User(  # 1
                name="Jim",
                password="j",
                is_admin=True,
                role_id=1,
            ),
            User(  # 2
                name="Kate",
                password="k",
                is_admin=True,
                role_id=1,
            ),
            User(  # 3
                name="Al",
                password="a",
                is_admin=True,
                role_id=1,
            ),
            User(  # 4
                name="a",
                password="a",
                is_admin=True,
                role_id=1,
            ),
        ]
    )

    #####################
    # RESPONSES: TYPE 2 #
    #####################
    db.session.add_all(
        [
            ResponseT2(  # 1
                user_id=1,
                assessment_id=1,
                t2_question_id=1,
                response_content="-m",
                is_correct=True,  # Don't think we need this?
            ),
            ResponseT2(  # 2
                user_id=1,
                assessment_id=1,
                t2_question_id=2,
                response_content="push",
                is_correct=True,
            ),
            ResponseT2(  # 3
                user_id=2,
                assessment_id=1,
                t2_question_id=1,
                response_content="-m",
                is_correct=True,
            ),
        ]
    )

    db.session.commit()
