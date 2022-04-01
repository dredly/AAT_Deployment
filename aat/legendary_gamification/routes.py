from click import option
from flask import copy_current_request_context, render_template, request, redirect, url_for
from flask_login import current_user
import flask_login
import random
from aat import db
from aat.legendary_gamification.forms import ChallengeForm
from . import legendary_gamification
from werkzeug.exceptions import BadRequestKeyError
from ..models import Achievement, Awarded_Achievement, Awarded_Badge, Badge, Challenge, ChallengeQuestions, QuestionT1, User, Option, Module

questions = ["How do you print things in python",
             "How do you declare a function in python",
             "How many mexicans does it take to unscrew a light bulb"]

options = [["System.out.println()", "console.log()", "print()", "just type it lol"], 
           ["jeff", "def", "deaf", "public static void main(String[] args)"],
           ["None", "one", "falsy", "Juan"]]

answers = [[False, False, True, False],
           [False, True, False, False],
           [False, False, False, True]]

question_counter = 0
challenge_questions = []
challenge_options = []

@legendary_gamification.route("/achievements", methods=["GET", "POST"])
def achievements():
    global challenge_questions
    global challenge_options
    badges = []
    achievements = []
    lines_ranks = []
    all_users = User.query.all()


    for user in all_users:
        assessment_marks = {}
        for response in user.t1_responses:
            if response.assessment not in assessment_marks:
                assessment_marks[response.assessment] = {
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
            else:
                assessment_marks[response.assessment]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks[response.assessment][
                    "marks_possible"
                ] += response.question.num_of_marks

        ## T2_responses
        for response in user.t2_responses:
            if response.assessment not in assessment_marks:
                assessment_marks[response.assessment] = {
                    "marks_awarded": response.question.num_of_marks
                    if response.is_correct
                    else 0,
                    "marks_possible": response.question.num_of_marks,
                }
            else:
                assessment_marks[response.assessment]["marks_awarded"] += (
                    response.question.num_of_marks if response.is_correct else 0
                )
                assessment_marks[response.assessment][
                    "marks_possible"
                ] += response.question.num_of_marks

        module_dict = {}

        for module in Module.query.all():
            for assessment, data in assessment_marks.items():
                if assessment.module_id == module.module_id:
                    if module not in module_dict:
                        module_dict[module] = {assessment: data}
                    else:
                        module_dict[module][assessment] = data

        sum_of_marks_awarded = 0
        sum_of_marks_possible = 0

        for module in module_dict:
            for assessment, data in assessment_marks.items():
                sum_of_marks_awarded += data["marks_awarded"]
                sum_of_marks_possible += data["marks_possible"]
                # module_dict[module]["marks_awarded"] += data["marks_awarded"]
                # module_dict[module]["marks_possible"] += data["marks_possible"]

        # if sum_of_marks_possible == 0:
        #     return render_template("no_questions_answered.html")

        overall_results = {
            "sum_of_marks_awarded": sum_of_marks_awarded,
            "sum_of_marks_possible": sum_of_marks_possible,
        }

        # print(user.name, overall_results)

        lines_ranks.append((overall_results['sum_of_marks_awarded'], user.name))

        module_totals = {}

        for module, module_details in module_dict.items():
            module_totals[module.title] = {"marks_awarded": 0, "marks_possible": 0}
            for assessment, assessment_details in module_details.items():
                module_totals[module.title]["marks_awarded"] += assessment_details[
                    "marks_awarded"
                ]
                module_totals[module.title]["marks_possible"] += assessment_details[
                    "marks_possible"
                ]

    # print(f"{module_totals=}")
    # print(lines_ranks)

    award_badges = Awarded_Badge.query.filter_by(user_id=current_user.id).all()
    # for awards in award_badges:
    #     print(awards.badge_id)
    award_achievements = Awarded_Achievement.query.filter_by(user_id=current_user.id).all()
    for awards in award_badges:
        badge = Badge.query.filter_by(badge_id=awards.badge_id).first()
        badges.append(badge)
    for awards in award_achievements:
        achievement = Achievement.query.filter_by(achievement_id=awards.achievement_id).first()
        achievements.append(achievement)
    
    in_challenges = Challenge.query.with_entities(Challenge.from_user, Challenge.to_user, Challenge.challenge_id, Challenge.difficulty).filter_by(to_user=current_user.id, active=0).all()
    out_challenges = Challenge.query.with_entities(Challenge.from_user, Challenge.to_user, Challenge.difficulty).filter_by(from_user=current_user.id, active=0).all()
    active_challenges = Challenge.query.filter_by(active=1).all()
    in_users = []
    out_users = []
    active_users = []
    challenge_ids = []
    incoming_challenge_difficulty = []
    outgoing_challenge_difficulty = []


    for challenge in in_challenges:
        user_from = User.query.filter_by(id=challenge[0]).first()
        in_users.append((user_from.id, user_from.name))
        challenge_ids.append(challenge[2])
        incoming_challenge_difficulty.append(challenge[3])
    for challenge in out_challenges:
        user_to = User.query.filter_by(id=challenge[1]).first()
        out_users.append((user_to.id, user_to.name))
        outgoing_challenge_difficulty.append(challenge[2])
    for challenge in active_challenges:
        if challenge.from_user == current_user.id:
            user = User.query.filter_by(id=challenge.to_user).first()
            difficulty = challenge.difficulty
            active_users.append((challenge.challenge_id, user.name, difficulty))
        elif challenge.to_user == current_user.id:
            user = User.query.filter_by(id=challenge.from_user).first()
            difficulty = challenge.difficulty
            active_users.append((challenge.challenge_id, user.name, difficulty))


    # print(in_users)
    # print(out_users)
    # print(active_users)
    challenge = ChallengeForm()

    # with open("aat/legendary_gamification/ranks.txt", 'r') as f:
    #     lines_ranks = f.readlines()
    # with open("aat/legendary_gamification/awards.txt", 'r') as f:
    #     lines_achievements = f.readlines()
    if request.method == "POST":
        try:
            choice = request.form['button']
        except:
            pass

        try:
            choice = request.form["accept_challenge_button"]
        except:
            pass

        try:
            choice = request.form["take_challenge_button"]
        except:
            pass
        if choice == "Practice Rapid Fire Tests" or choice == "Take Rank Up Test":
                questions_t1 = QuestionT1.query.all()
                max_questions = len(questions_t1)
                question_ids = []
                while len(question_ids) < 3:
                    q_id = random.randrange(1, max_questions+1)
                    if q_id not in question_ids:
                        question_ids.append(q_id)
                for i in question_ids:
                    question = QuestionT1.query.with_entities(QuestionT1.q_t1_id, QuestionT1.question_text).filter_by(q_t1_id=i).first()
                    challenge_questions.append(question)
                for i in question_ids:
                    option = Option.query.with_entities(Option.option_id, Option.option_text, Option.is_correct).filter_by(q_t1_id=i).all()
                    challenge_options.append(option)

                return redirect(url_for(".rapid_fire"))

        elif choice == "Challenge User":
            challenge_details = Challenge(from_user=current_user.id, to_user=int(request.form.get("Users")), difficulty=int(challenge.difficulty.data))
            db.session.add(challenge_details)
            db.session.commit()
            return redirect("redirect-page-achievement")
        elif choice == "Accept Challenge":
            try:
                chosen_challenge = request.form['accept_options']
                challenge_active = Challenge.query.filter_by(challenge_id=chosen_challenge).first()
                challenge_active.active = 1
                db.session.add(challenge_active)
                db.session.commit()
                questions_t1 = QuestionT1.query.all()
                max_questions = len(questions_t1)
                question_ids = []
                while len(question_ids) < 3:
                    q_id = random.randrange(1, max_questions+1)
                    if q_id not in question_ids:
                        question_ids.append(q_id)
                for i in question_ids:
                    question = ChallengeQuestions(challenge_id=chosen_challenge, question_id=i)
                    db.session.add(question)
                    db.session.commit()

                return redirect("redirect-page-achievement")
            except BadRequestKeyError:
                pass
        elif choice == "Take Challenge":
            try:
                chosen_challenge = request.form['active_options']
                challenge_taken_id = Challenge.query.filter_by(challenge_id=chosen_challenge).first()
                challenge_question_all = ChallengeQuestions.query.filter_by(challenge_id=chosen_challenge).all()

                for question in challenge_question_all:
                    question = QuestionT1.query.with_entities(QuestionT1.q_t1_id, QuestionT1.question_text).filter_by(q_t1_id=question.question_id).first()
                    challenge_questions.append(question)
                # print(challenge_questions)
                for question in challenge_question_all:
                    option = Option.query.with_entities(Option.option_id, Option.option_text, Option.is_correct).filter_by(q_t1_id=question.question_id).all()
                    challenge_options.append(option)
                # print(challenge_options)
                return redirect(url_for(".rapid_fire", challenge_questions=challenge_questions, challenge_options=challenge_options))
            except BadRequestKeyError:
                pass           
    return render_template(
        "achievements.html", ranks=sorted(lines_ranks, key=lambda x: x[0], reverse=True), badges=badges,
        achievements=achievements, incoming_challenges=in_users, outgoing_challenges=out_users, challenge=challenge,
        all_users=all_users, challenge_ids=challenge_ids, in_difficulty=incoming_challenge_difficulty,
        out_difficulty=outgoing_challenge_difficulty, active_users=active_users
        )


@legendary_gamification.route("/redirect-page-achievement")
def refresh():
    return redirect("achievements")


@legendary_gamification.route("/correctement")
def correct_answer():
    global question_counter
    question_counter += 1
    return redirect("rapid-fire")


@legendary_gamification.route("/rapid-fire-victory-royale", methods=['GET', 'POST'])
def assessment_success():
    global question_counter
    global challenge_questions
    global challenge_options
    if request.method == "POST":
        try:
            choice = request.form['button']
        except BadRequestKeyError:
            return redirect("rapid-fire-victory-royale")
        question_counter = 0
        challenge_questions = []
        challenge_options = []
        if choice  == "reset":
            return redirect("rapid-fire")
        elif choice == "return":
            return redirect("achievements")
    return render_template("assess_success.html")

@legendary_gamification.route("/tortement")
def wrong_answer():
    return render_template("wrong_answer.html")


@legendary_gamification.route("/level-up")
def level_up():
    return render_template("levelup.html")


@legendary_gamification.route("/rapid-fire", methods=["GET", "POST"])
def rapid_fire():
    global question_counter
    try:
        if request.method == "POST":
            try:
                choice = request.form['options']
                if choice == "True":
                    return redirect("correctement")
                else:
                    return redirect("tortement")
            except BadRequestKeyError:
                return redirect("tortement")
            
        return render_template("fire.html", question=challenge_questions[question_counter], options=challenge_options[question_counter], question_counter=question_counter)
    except IndexError:
        return redirect("rapid-fire-victory-royale")


@legendary_gamification.route("/profile-page")
def profile():
    badges = []
    achievements = []
    award_badges = Awarded_Badge.query.filter_by(user_id=current_user.id).all()
    print(current_user.id)
    # for awards in award_badges:
    #     print(awards.badge_id)
    print(award_badges)
    award_achievements = Awarded_Achievement.query.filter_by(user_id=current_user.id).all()
    print(award_achievements)
    for awards in award_badges:
        badge = Badge.query.filter_by(badge_id=awards.badge_id).first()
        badges.append(badge)
        print("Added")
    for awards in award_achievements:
        achievement = Achievement.query.filter_by(achievement_id=awards.achievement_id).first()
        achievements.append(achievement)
    for badge in badges:
        print(badge.name)
    return render_template("profile.html", badges=badges, achievements=achievements)