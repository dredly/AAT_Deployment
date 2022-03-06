from flask import render_template, request, redirect
from . import legendary_gamification

questions = ["How do you print things in python", "How do you declare a function in python"]
options = [["System.out.println()", "console.log()", "print()", "just type it lol"], ["jeff", "deaf", "def", "public static void main(String[] args)"]]

question_counter = 0

@legendary_gamification.route("/achievements")
def achievements():
    return render_template("achievements.html")


@legendary_gamification.route("/correctement")
def correct_answer():
    global question_counter
    question_counter += 1
    return redirect("rapid-fire")


@legendary_gamification.route("/tortement")
def wrong_answer():
    return render_template("wrong_answer.html")


@legendary_gamification.route("/level-up")
def level_up():
    return render_template("levelup.html")


@legendary_gamification.route("/rapid-fire", methods=["GET", "POST"])
def rapid_fire():
    global question_counter
    if request.method == "POST":
        choice = request.form['options']
        if choice == "option3":
            return redirect("correctement")
        else:
            return redirect("tortement")
    if question_counter < len(questions):
        return render_template("fire.html", question=questions[question_counter], options=options[question_counter], question_counter=question_counter)
    else:
        return render_template("fire.html", question=questions[0], options=options[0], question_counter=question_counter)
