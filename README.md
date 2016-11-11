[![Build Status](https://travis-ci.org/SRJ9/django-driver27.svg?branch=develop)](https://travis-ci.org/SRJ9/django-driver27)
[![codecov](https://codecov.io/gh/SRJ9/django-driver27/branch/develop/graph/badge.svg)](https://codecov.io/gh/SRJ9/django-driver27)
[![Code Climate](https://codeclimate.com/github/SRJ9/django-driver27/badges/gpa.svg)](https://codeclimate.com/github/SRJ9/django-driver27)
[![Requirements Status](https://requires.io/github/SRJ9/django-driver27/requirements.svg?branch=develop)](https://requires.io/github/SRJ9/django-driver27/requirements/?branch=develop)

# driver27
Racing competition manager in Django where you can manage different
motor competitions with its own punctuation rules, races, drivers, teams
which, at the same time, can be part of multiple competitions.

Modify your settings.py
=======================
```
INSTALLED_APPS = [
    'bootstrap3',
...
    'django_countries',
    'tabbed_admin',
    'driver27'
]


TABBED_ADMIN_USE_JQUERY_UI = True
```

Versions
========
- 0.14c (Fernando Alonso 14)
- 0.16c (Race to Championship '16)
- 0.27-VIL (Gilles Villeneuve 27)

0.16
====
- What would happen if the 10-point scoring system was used? Would the champion be the same? This version will give you the answer.
- Olympic rank: Alternative rank with the gold first method. The driver with superior race results (based on descending order, from number of wins to numbers of second-places down) will gain precedence.
- Road to championship: When the season goes down, we can calculate who would be the champion predicting the results in the last races. Olympic rank is counted in case of points tie. Rosberg or Hamilton?

0.14
====
- Initial models
- Basic relation restriction with exceptions and tests
- Basic templates to frontend views
- Basic demo to test the app

models
===========
- Driver
- Team
- Circuit
- Grand Prix
- Competition
- Season
- Race
- Result
- Contender (Driver/Competition relation)
- Seat (Contender/Team relation)
- fixtures folder contains fixture of each model to demo project.

Demo (virtuaenv recomended)
===========================
```bash
$ git clone https://github.com/SRJ9/django-driver27
$ cd django-driver27 # or name of destiny folder
$ pip install -r requirements.txt
$ python demo/manage.py runserver
$ # login /admin: admin:pass
```

Todo
====
- [ ] Add records by season, driver, team, competition
- [ ] Add drivers profile with records, last_wins, teams...
- [x] Add easy clone to Season
- [ ] Translate
- [ ] 1980's punctuation. Only 11 best results.
- [ ] Old punctuation. Split season races, and get only 4 of each half.

# History
Driver 27 is a reference to car number of Gilles Villeneuve, F1 Driver died in 1982. Gilles is considered one of best driver despite he never won the World Championship, something that Jacques Villeneuve, his son, did in 1998.

In 1980's decade, F1 teams kept their numbers unless they were champions. This made Ferrari, the most legendary team of the F1, take that number for many years (1981-1995), making the number an icon of this sport.
