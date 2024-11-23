import subprocess

class Linter:

    def __init__(self):
        self.info = None
        
    
    def validate(self, file_path: str) -> bool:
        '''
        Cтатический анализ стилистики кода, находящегося по пути file_path
        '''

        # Расширение файла
        file_extension = file_path.split('.')[-1]

        # Все пути к линтерам
        linterpath = {
            "py"  : "flake8",
            "c"   : "cpplint",
            "cpp" : "cpplint ",
            "go"  : "./Promo/src/Promo/linters/go/golangci-lint run",
            "rs"  : "./Promo/src/Promo/linters/rust/.cargo/bin/rustfmt --check"
        }
        
        # Создание команды и запуск субпроцесса с соответствующим линтером
        command = f"{linterpath[file_extension]} {file_path}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # print(result)
        # Проверка на наличие ошибок в загруженном файле
        if result.returncode == 0:
            # Файл прошел проверку без ошибок
            self.info = ["Ваш код стилистически идеален😋"]
            return True
        else:
            # В файле найдены ошибки
            self.info = result.stdout.decode('utf-8').split("\n")
            return False
