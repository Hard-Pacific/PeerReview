import subprocess

class AutoTest:
    def __init__(self):
        self.info = None

    def validate(self, input, answer, file_path):
        # Запуск программы и передача аргументов
        process = subprocess.Popen(
            ["python", file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,  # Получить стандартный вывод
            stderr=subprocess.PIPE   # Получить стандартный поток ошибок
        )

        # Получение вывода и ошибок
        stdout, stderr = process.communicate(input=input.encode())
        if stdout.decode()[:-2] != answer:
            self.info = ["Автотест не прошел успешно"]
        else:
            self.info = ["Автотест прошел успешно"]

        return stdout.decode()[:-2] == answer
