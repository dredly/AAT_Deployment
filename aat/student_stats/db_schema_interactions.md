# How student stats will work

# ALL BELOW IS FOR ONE STUDENT
# TODO: get student log-in details
Snipped from previous coursework:
{% if current_user.is_authenticated %}
    {{current_user.first_name }}
{% else %}
    Guest
{% endif %}
# TODO: get list of all modules for student

- works for "Jim", but not for a new user "a"

# TODO: get list of all assessments for student
# TODO: get list of all questions for student
# TODO: get list of all responses for student

(This is more a question to remind myself)
what would be the code (HTML/Jinja2) for "if user is a student then <p>STUDENT</p> else <p>LECTURER</p>


# Qs

- Assume all students are on the same course
  - Therefore have the same modules

- models.py > Module
  - "assessment" used, should be "assessments"
  - Unsure if this matters:
    - All table names should start with capitals ("Users", "Achievements" etc.) (and possibly should be plural? Unsure, is for classes, don't know for table names)