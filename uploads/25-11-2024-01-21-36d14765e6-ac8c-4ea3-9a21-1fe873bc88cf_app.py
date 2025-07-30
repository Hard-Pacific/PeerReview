from flask import Flask
from flask import render_template
from flask import request
from flask import flash
import uuid
from requirments import Requirement
from linter import Linter
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "скибиди"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def peer_review():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            # Считываем имя файла и сам файл
            filename = file.filename
            file = request.files["file"]

            # Создаем уникальный префикс с датой и сохраняем файл
            unique_prefix = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + str(uuid.uuid4())
            filename = f"{unique_prefix}_{secure_filename(filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            file_path = app.config["UPLOAD_FOLDER"]+"/"+filename

            # Peer проверка
            result = []
            req = Requirement()
            req.validate(file_path=file_path, ban_list=["for"], demand=["if"])

            lint = Linter()
            lint.validate(file_path)

            result.extend(lint.info)
            result.extend(req.info)

            with open(file_path) as P:
                code = P.read()
            return render_template("index.html", text=result, code=code)

    return render_template("index.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True)
