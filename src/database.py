import sqlite3 as sq
from typing import Optional, Tuple, List

class DataBase:
    def __init__(self, db_name: str = "users.db"):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        """Инициализирует базу данных и создает таблицы при необходимости"""
        with self._get_connection() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    login TEXT UNIQUE NOT NULL,
                    mail TEXT UNIQUE NOT NULL,
                    passwd TEXT NOT NULL
                );
                """
            )

    def _get_connection(self):
        """Возвращает соединение с базой данных"""
        return sq.connect(self.db_name)

    def add_student(self, login: str, passwd: str, mail: str) -> bool:
        """Добавляет нового студента в базу данных"""
        try:
            with self._get_connection() as con:
                con.execute(
                    "INSERT INTO students VALUES (?, ?, ?);", 
                    (login, mail, passwd)
                )
                return True
        except sq.IntegrityError:
            # Логин или почта уже существуют
            return False

    def delete_student(self, login: str) -> bool:
        """Удаляет студента по логину"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "DELETE FROM students WHERE login = ?", 
                (login,)
            )
            return cursor.rowcount > 0

    def update_login(self, old_login: str, new_login: str) -> bool:
        """Обновляет логин студента"""
        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE students SET login = ? WHERE login = ?", 
                    (new_login, old_login)
                )
                return cursor.rowcount > 0
        except sq.IntegrityError:
            # Новый логин уже занят
            return False

    def update_password(self, login: str, new_passwd: str) -> bool:
        """Обновляет пароль студента по логину"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "UPDATE students SET passwd = ? WHERE login = ?", 
                (new_passwd, login)
            )
            return cursor.rowcount > 0

    def update_email(self, login: str, new_mail: str) -> bool:
        """Обновляет email студента по логину"""
        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE students SET mail = ? WHERE login = ?", 
                    (new_mail, login)
                )
                return cursor.rowcount > 0
        except sq.IntegrityError:
            # Новый email уже занят
            return False

    def check_credentials(self, login: str, passwd: str) -> bool:
        """Проверяет правильность логина и пароля"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT 1 FROM students WHERE login = ? AND passwd = ?", 
                (login, passwd)
            )
            return cursor.fetchone() is not None

    def get_student(self, login: str) -> Optional[Tuple]:
        """Возвращает данные студента по логину"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE login = ?", 
                (login,)
            )
            return cursor.fetchone()

    def get_all_students(self) -> List[Tuple]:
        """Возвращает список всех студентов"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM students")
            return cursor.fetchall()
        
    # def fetch_students(self):
    #     con = sq.connect("data.db")
    #     cursor = con.cursor()
    #     cursor.execute("SELECT * FROM students")
    #     return cursor.fetchall()

data = DataBase()
data.add_student('alex', '234', '234234234')
# data.replace_login('alex', 'alexander')
print(data.check_credentials('Alexander', '234'))
# data.delete_student('alex')