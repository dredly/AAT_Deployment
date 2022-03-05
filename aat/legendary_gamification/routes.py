from flask import render_template
from . import legendary_gamification


@legendary_gamification.route("/achievements")
def achievements():
    return render_template("achievements.html")


@legendary_gamification.route("/level-up")
def level_up():
    return render_template("levelup.html")


@legendary_gamification.route("/rapid-fire")
def rapid_fire():
    return render_template("fire.html")
