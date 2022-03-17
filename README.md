# Automated Assessment Tool
by Team S

[[_TOC_]]

## TEAM ETHOS:
PIZZA FOR ALL

## DEVELOPER PRACTICES:
Page titles can either be defined by:
- overwriting the {% block title %} i.e. in your template putting {% block title %}My Page Title{% endblock %}
- in routes.py defining the variable "title". This will then become the page's title.

Commit message format to follow Git principles:

https://git.kernel.org/pub/scm/git/git.git/tree/Documentation/SubmittingPatches?id=HEAD#n133
https://stackoverflow.com/questions/3580013/should-i-use-past-or-present-tense-in-git-commit-messages

```git
[Verb] [Noun]
Description
```

i.e.
```git
Finish Coursework
We finished the coursework. Yay.
```

- TODO: look into relationship between commit messages and issues
( #7 [text] -> relates to issue #7 )

- Everyone make their own sandbox GitLab project to explore functionality.

Good use of Git branches
- Never work on 'main'
- Always work on 'your branch'
- Always pull to 'your branch' from 'main' before pushing/merging to main
- Always delete 'your branch' after merging (i.e. leave the default)

Keep Git repo ONLY for project files
Use Teams for storing supporting files (i.e. images/pdfs/etc.)

Reduce likelihood of single points of failure
Everyone to be aware of everything all of the time

Code to look good (apply PEP8 principles: https://www.python.org/dev/peps/pep-0008/)

Please use formatter "Black" on code
https://pypi.org/project/black/

Keep requirements.txt up-to-date
- If adding to requirements.txt, please tell everyone (/add to commit message)

Secret keys = Environment variables for security

Documentation to be updated regularly.
- Wiki (GitLab)
-- External

- Docstrings
-- Internal

## TECH STACK:

- Front-end: HTML/CSS/JS - opt. dedicated framework (tbc.)
- Back-end: Flask (Python) - using Blueprints etc.
- Database: MySQL (uni server) / AbSQL (totally a thing)
- Deployment: OpenShift
- Test framework: PyTest (built-in for Flask)

## SCHEDULED MEETINGS:

OPTIONAL Monday meeting (11am-12pm): Online
- Time for use as and when required 
-- Could be for paired work or general chats

Wednesday (11am-1pm): Big Room => Turing Suite
- 30 mins: team meeting
- 60 mins: pair programming
- 30 mins: team meeting

Friday (9am-1pm): Online
- Test cases
-- Max 7 test cases (NO MORE TESTS ALLOWED)

## FEATURES TO CODE:

Each feature will have a Lead and a Second.
This is to prevent single points of failure.

[ Lead > Second ]

1. Add (edit & delete) T1 Q [ Alex > Lins ]
2. Add (edit & delete) T2 Q [ Dan > Jake ]
3. Add (edit & delete) Summative/Formative Assessment [ Matt > Rich ]
4. Student Take Assessment [ Lins > Abs ]
5. Staff Review Statistics [ Jake > Alex ]
6. Student Review Statistics [ Rich > Dan ]
7. Advanced/Updated/Legendary Gamification [ Abs > Matt ]

Definitions:

- A question must consist of at least:
-- question
-- answer
-- correctness check
-- feedback

- T1: Multiple choice & True/False
- T2: Text input

## LINKS TO WATCH:
Creating Class Diagrams (CRC cards)
https://www.linkedin.com/learning/programming-foundations-object-oriented-design-3/creating-class-diagrams-attributes

Blueprints:
https://flask.palletsprojects.com/en/1.1.x/blueprints/

### Commit message templates

- https://gist.github.com/lisawolderiksen/a7b99d94c92c6671181611be1641c733
- https://thoughtbot.com/blog/better-commit-messages-with-a-gitmessage-template
- https://thoughtbot.com/blog/write-good-commit-messages-by-blaming-others
- https://thoughtbot.com/blog/5-useful-tips-for-a-better-commit-message

### Nice to haves

- look into GitLab functionality
    - Milestones
    - CI/CD
- tailored feedback based on specific mistake types

- web-based, desktop (Linux for Abs) and PS4OS
- order a Sony PS SDK
    - Run "Doom" in the AAT
    - soundtrack
    - speed mode 
    - boss rush (Magrit)

- secondary economy through data sales
    - ad space/microtransactions
    - lootboxes
    - nft support
    - aatcoin

- Q2
    - add input of code?





