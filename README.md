# CLnotes V1.0.0

## A project written in Python using the Django framework to manage school classes and classes outside of school.

This is a **Web Application** project, that is build for **[Kharazmi festival](https://en.wikipedia.org/wiki/Khwarizmi_International_Award)** (A competition between all of students from 7th 9th grade) , using **Python** and **Django** framework, with goal of making relationship between students and teachers easier and better.

### Capabilities ✅ :

* Create classes, and invite students and teachers to the class
* Create and edit Homeworks
* Submit result of homework for teacher (creator) of that homework
* Submit feedback of students result of a homework
* Create and edit Exams
* Submit result of exam for each assigned student to that exam
* Submit feedback of teacher result of an exam

### Future Plans 📅 :

* Create and edit notes for students in a class
* Create and edit sample questions for students in a class
* Create and edit TODO list for your self
* Create and edit a plan for studying in a calender
* An AI which analyze your homeworks, exams, notes, sample questions and your TODO list for helping you in making your studying plan
* An AI which analyze homework, exam. notes and sample questions of a teacher and make you some sample questions for you next exam
* Ranking students in classes
* Login and register via Gmail
* Login and register via SMS
* Compatibility with every language

## How to install 📖 :

1. Clone the Repository
2. Go to project Root
3. Install Python latest version
4. Open a Terminal
5. Create a Virtual Environment using this Command: ```python3 -m venv venv```
6. Active Virtual Environment using this Command: ```.\venv\Scripts\active``` (For windows)
7. Active Virtual Environment using this Command: ```source venv/bin/activate``` (For Linux)
8. Install Requirements using this Command: ```pip install -r requirements.txt```
9. For changing Default language, open CLnotess/settings.py and find "LANGUAGE_CODE" (default is persian)
10. Run Project: ```python manage.py runserver```
11. Open your browser and navigate to: ```127.0.0.1:8000```

# Commands ⌨️ :

1. Add default lessons: ```python manage.py add_lessons``` (They are in persian)
2. Create superuser: ```python manage.py createsuperuser```
3. run the project: ```python manage.py runserver```

## Find a bug 🐞 ?
If you found some issues in CLnotess, before submitting it in **[issue page](https://github.com/MatinAbedini/CLnotess/issues)**, make sure that its not created in the past (Check open and closed issues), also before submitting a PR fix for a bug, make sure you have created an issue for that bug.
