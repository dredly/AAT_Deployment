from flask import copy_current_request_context, render_template, request, redirect
from flask_login import current_user
import flask_login

from aat.legendary_gamification.forms import ChallengeForm
from . import legendary_gamification
from werkzeug.exceptions import BadRequestKeyError
from ..models import Achievement, Awarded_Achievement, Awarded_Badge, Badge, Challenge, User

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

@legendary_gamification.route("/achievements", methods=["GET", "POST"])
def achievements():
    badges = []
    achievements = []
    all_users = User.query.all()
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
    
    in_challenges = Challenge.query.with_entities(Challenge.from_user, Challenge.to_user).filter_by(to_user=current_user.id).all()
    out_challenges = Challenge.query.with_entities(Challenge.from_user, Challenge.to_user).filter_by(from_user=current_user.id).all()
    in_users = []
    out_users = []


    print(in_challenges)
    print(out_challenges)
    for challenge in in_challenges:
        user_from = User.query.filter_by(id=challenge[0]).first()
        in_users.append(user_from.name)
    for challenge in out_challenges:
        user_to = User.query.filter_by(id=challenge[1]).first()
        out_users.append(user_to.name)

    print(in_users)
    print(out_users)
    challenge = ChallengeForm()

    with open("aat/legendary_gamification/ranks.txt", 'r') as f:
        lines_ranks = f.readlines()
    with open("aat/legendary_gamification/awards.txt", 'r') as f:
        lines_achievements = f.readlines()
    if request.method == "POST":
        return redirect("rapid-fire")
    return render_template(
        "achievements.html", ranks=sorted(lines_ranks), awards=lines_achievements, badges=badges,
        achievements=achievements, incoming_challenges=in_users, outgoing_challenges=out_users, challenge=challenge,
        all_users=all_users
        )


@legendary_gamification.route("/correctement")
def correct_answer():
    global question_counter
    question_counter += 1
    return redirect("rapid-fire")


@legendary_gamification.route("/rapid-fire-victory-royale", methods=['GET', 'POST'])
def assessment_success():
    global question_counter
    if request.method == "POST":
        try:
            choice = request.form['button']
        except BadRequestKeyError:
            return redirect("rapid-fire-victory-royale")
        question_counter = 0
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
    try:
        global question_counter
        if request.method == "POST":
            try:
                choice = request.form['options']
            except BadRequestKeyError:
                return redirect("tortement")
            if answers[question_counter][int(choice)]:
                return redirect("correctement")
            else:
                return redirect("tortement")
        return render_template("fire.html", question=questions[question_counter], options=options[question_counter], question_counter=question_counter)
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