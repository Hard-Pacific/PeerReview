from flask import Flask
from flask import render_template
from flask import request
from requirments import Requirement
from linter import lint_file
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] =    UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем файл из запроса
        file = request.files['file']
        if file:
            filename = file.filename
            filename = "file" + filename[filename.find("."):]
            # Сохраняем файл
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(app.config['UPLOAD_FOLDER']+"/"+filename)
            req = Requirement.check(filename=app.config['UPLOAD_FOLDER']+"/"+filename, ban=["for"], demand=["if"])
            print(0)
            lint = lint_file(filename)
            print(1)
            result = { req:"requerments", lint:"linter"}
            print(2)
            print(result)
            return render_template('index.html', text=result)

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)