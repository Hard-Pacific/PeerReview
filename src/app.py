from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from requirments import Requirement
from datetime import datetime
from autotest import AutoTest
from linter import Linter
import database as db
import uuid
import os


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        session['user_id'] = username
        # Валидация формы
        if not username or not email or not password or not confirm_password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        
        # БД ЧАСТЬ
        db.data.add_user(username, password, email)
        print("-------------Данные пользователя зарегистрированы----------")

        return redirect(url_for('index'))
        # БД ЧАСТЬ
    return render_template('register.html')

# Определяет (не)активную сессию
@app.route("/", methods=["GET", "POST"])
def welcome():
    if "user_id" in session:
        return render_template("index.html", username=session["user_id"])
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("register.html")

@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Получаем файл из запроса
        file = request.files["file"]
        if file:
            # Считываем имя файла и сам файл
            filename = file.filename
            file = request.files["file"]

            # Создаем уникальный префикс с датой и сохраняем файл
            unique_prefix = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + str(
                uuid.uuid4()
            )
            filename = f"{unique_prefix}_{secure_filename(filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            file_path = app.config["UPLOAD_FOLDER"] + "/" + filename
            print("AOFAIFJASODJAS:LA")
            # Peer проверка
            result = []

            req = Requirement()
            req.validate(file_path=file_path,
                         ban_list=["for"],
                         demand_list=["for"])

            lint = Linter()
            lint.validate(file_path)

            test = AutoTest()
            test.validate("10", "12", file_path)

            result.extend(lint.info)
            result.extend(req.info)
            result.extend(test.info)

            with open(file_path, encoding="utf-8") as P:
                code = P.read()
            return render_template("index.html", text=result, code=code, username=session['user_id'])

    return render_template("index.html", username=session['user_id'])


@app.route("/allcourses")
def allcourses():
    items = [{"name": course["title"], "url": f"/{course["title"]}"} for course in db.data.get_all_courses()]
    return render_template("allcourses.html", items=items, courses="Все")

@app.route("/mycourses")
def mycourses():
    items = [{"name": course["title"], "url": f"/{course["title"]}"} for course in db.data.get_all_courses()]
    return render_template("allcourses.html", items=items, courses="Мои")


@app.route("/<course>")
def course(course):
    if request.method == "POST":
        task_info = db.get_task(course)
        return render_template("task.html", items=task_info, courses="Мои", do=True)
    items = [{"name": task["title"]} for task in db.data.get_course_tasks(course)]
    return render_template("allcourses.html", items=items, courses="Мои", course_name=course, do=True)

@app.route("/mycourses/<tempcourse>")
def tempcourse(tempcourse):
    items = [
        {"name": "Вывод", "url": "/mycourses/tempcourse/Вывод"},
        {"name": "Условия", "url": "/mycourses/tempcourse/Условия"},
        {"name": "Циклы", "url": "/mycourses/tempcourse/Циклы"}
    ]
    return render_template("tempcourse.html", items=items)

@app.route("/<tempcourse>/<task>", methods=["GET", "POST"])
def task(tempcourse, task):
    task_info = db.data.get_task(task_name=task, course_name=tempcourse)
    title = task_info["title"]
    description = task_info["description"]
    if request.method == "POST":
        # Получаем файл из запроса
        file = request.files["file"]
        if file:
            # Считываем имя файла и сам файл
            filename = file.filename
            file = request.files["file"]

            # Создаем уникальный префикс с датой и сохраняем файл
            unique_prefix = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + str(
                uuid.uuid4()
            )
            filename = f"{unique_prefix}_{secure_filename(filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            file_path = app.config["UPLOAD_FOLDER"] + "/" + filename

            # Peer проверка
            result = []

            req = Requirement()
            req.validate(file_path=file_path,
                         ban_list=["for"],
                         demand_list=[])

            lint = Linter()
            lint.validate(file_path)

            test = AutoTest()
            test.validate("10", "12", file_path)

            result.extend(lint.info)
            result.extend(req.info)
            result.extend(test.info)

            with open(file_path, encoding="utf-8") as P:
                code = P.read()
            return render_template("task.html", text=result, code=code, title=title, description=description)

    return render_template("task.html", title=title, description=description)


@app.route("/create/<course_title>", methods=["GET", "POST"])
def create(course_title):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        input_data = request.form.get('input_data', '')
        output_data = request.form.get('output_data', '')
        demand_list = request.form.get('demand_list', '')

        db.data.add_task(course_title=course_title,
                         task_title=title,
                         input_data=input_data,
                         output_data=output_data,
                         demand_list=demand_list,
                         description=description)
        
        return redirect(url_for('create', course_title=course_title))

    tasks = db.data.get_course_tasks(course_title)
    print(tasks)

    return render_template('create.html', tasks=tasks)

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description']
        # БД ЧАСТЬ
        db.data.add_course(name, session["user_id"], description)
        return redirect(url_for('create', course_title=name))
    return render_template("new.html")


if __name__ == "__main__":
    app.run(debug=True)
    
