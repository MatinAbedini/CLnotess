# CLnotes 0.0.0

## A project written in Python using the Django framework to manage school classes and classes outside of school.

This is a **Web Application** project, that is build for **[Kharazmi festival](https://en.wikipedia.org/wiki/Khwarizmi_International_Award)** (A competition between all of students from 7th 9th grade) , using **Python** and the **Django** framework to make the relationship between students and teachers easier.

### Capabilities

* Create and edit Classes
* Create and edit Homeworks (For your self or for students in a class)
* Create and edit Exams (For your self or for students in a class)
* Set results for exams which are created by you (For each assigned students)
* Set results for assigned Homeworks

## How to install:

1. Clone the Repository
2. Go to project Root
3. Install Python
4. Open a Terminal
5. Create a Virtual Environment using this Command: ```python3 -m venv venv```
6. Active Virtual Environment using this Command: ```.\venv\Scripts\active``` (For windows)
7. Active Virtual Environment using this Command: ```source venv/bin/activate``` (For Linux)
8. Install Requirements using this Command: ```pip install -r requirements.txt```
9. Apply Migrations: ```python manage.py migrate```
10. Run Project: ```python manage.py runserver```
11. Open your browser and navigate to: ```127.0.0.1:8000```

## Find a bug ?
If you found an issue or would like to submit improvements to this project, please make an issue using Issues tab. If you want to submit a Pull Request Fix, make sure you create an issue in Issues tab.

## Known Issues

1. Detail pages frontend are not working
2. Sidebar links are not working
3. Classes list page are not working
