from flask import render_template, request, redirect
from . import legendary_gamification

question = "How do you print things in python"
options = ["System.out.println()", "console.log()", "print()", "just type it lol"]

@legendary_gamification.route("/achievements", methods=["GET", "POST"])
def achievements():
    if request.method == "POST":
        choice = request.form['options']
        if choice == "option3":
            return redirect("correctement")
    return render_template("achievements.html", question=question, options=options)


@legendary_gamification.route("/correctement")
def correct_answer():
    return render_template("correct_answer.html")


@legendary_gamification.route("/level-up")
def level_up():
    return render_template("levelup.html")


@legendary_gamification.route("/rapid-fire")
def rapid_fire():
    return render_template("fire.html")
