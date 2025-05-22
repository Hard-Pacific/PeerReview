import subprocess
import sys
import re


class Linter:

    def __init__(self):
        self.info = None

    def validate(self, file_path: str):
        """
        Cтатический анализ стилистики кода, находящегося по пути file_path
        """

        # Расширение файла
        file_extension = file_path.split(".")[-1]

        # Все пути к линтерам
        linterpath = {
            "py": "flake8",
            "c": "cpplint",
            "cpp": "cpplint ",
            "go": "./src/linters/go/golangci-lint run",
            "rs": "./src/linters/rust/.cargo/bin/rustfmt --check",
        }

        # Создание команды и запуск субпроцесса с соответствующим линтером
        command = f"{linterpath[file_extension]} {file_path}"
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        print(result)
        # Проверка на наличие ошибок в загруженном файле
        if result.returncode == 0:
            # Файл прошел проверку без ошибок
            self.info = ["Ваш код стилистически идеален"]
            return True
        else:
            # В файле найдены ошибки
            self.info = result.stdout.decode("utf-8").split("\n")
            self.info = Linter.prettier(self.info, "py")

            return False

    def prettier(error_list: list, file_extension: str):
        if file_extension == "py":
            pattern = r"(.+?):(\d+):(\d+): (.+)"
            group1 = 2
            group2 = 4
        elif file_extension == "c" or file_extension == "cpp":
            pattern = r"(.+):(\d+): (.+)"
            group1 = 2
            group2 = 3
        result = {}
        for error in error_list:
            match = re.match(pattern, error)
            if match:
                result[match.group(group1)] = match.group(group2)
        return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Необходимо указать путь к файлу")
        sys.exit(1)

    file_path = sys.argv[1]
    file = Linter()
    file.validate(file_path)
    print(file.info)
