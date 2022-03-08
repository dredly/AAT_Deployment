from flask import render_template, request, redirect
from . import legendary_gamification
from werkzeug.exceptions import BadRequestKeyError

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
    with open("aat/legendary_gamification/ranks.txt", 'r') as f:
        lines = f.readlines()
    if request.method == "POST":
        return redirect("rapid-fire")
    return render_template("achievements.html", ranks=sorted(lines))


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
