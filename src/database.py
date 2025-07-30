import sqlite3 as sq
from typing import Optional, List, Dict, Tuple
from passlib.hash import pbkdf2_sha256
import json

class EducationDB:
    def __init__(self, db_name: str = "education.db"):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):

        """Инициализирует все таблицы базы данных"""

        with self._get_connection() as con:
            # Таблица пользователей
            con.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    login TEXT UNIQUE NOT NULL,
                    mail TEXT UNIQUE NOT NULL,
                    passwd TEXT NOT NULL
                );
            """)

            # Таблица курсов
            con.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    title TEXT UNIQUE NOT NULL,
                    description TEXT,
                    owner_login TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (owner_login) REFERENCES users(login)
                );
            """)

            # Таблица заданий
            con.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    course_title TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    requirements TEXT,
                    FOREIGN KEY (course_title) REFERENCES courses(title) ON DELETE CASCADE
                );
            """)

            # Таблица записанных на курсы пользователей
            con.execute("""
                CREATE TABLE IF NOT EXISTS user_courses (
                    user_login TEXT NOT NULL,
                    course_title TEXT NOT NULL,
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_login, course_title),
                    FOREIGN KEY (user_login) REFERENCES users(login),
                    FOREIGN KEY (course_title) REFERENCES courses(course_title)
                );
            """)

            # Таблица отслеживания прогресса выполнения заданий пользователем
            con.execute("""
                CREATE TABLE IF NOT EXISTS task_progress (
                    user_login TEXT NOT NULL,
                    course_title TEXT NOT NULL,
                    task_title TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (user_login, course_title, task_title),
                    FOREIGN KEY (user_login) REFERENCES users(login) ON DELETE CASCADE,
                    FOREIGN KEY (course_title) REFERENCES courses(title) ON DELETE CASCADE,
                    FOREIGN KEY (course_title, task_title) REFERENCES tasks(course_title, title) ON DELETE CASCADE
                );
            """)

            # Создаем индексы
            con.execute("CREATE INDEX IF NOT EXISTS idx_users_login ON users(login);")
            con.execute("CREATE INDEX IF NOT EXISTS idx_courses_owner ON courses(owner_login);")
            con.execute("CREATE INDEX IF NOT EXISTS idx_tasks_course ON tasks(course_title);")

    def _get_connection(self):

        """Возвращает соединение с базой данных"""

        return sq.connect(self.db_name)

    # ===== Методы для работы с пользователями =====
    def add_user(self, login: str, passwd: str, mail: str) -> bool:

        """Добавляет нового пользователя с хешированным паролем"""

        try:
            # Хешируем пароль
            hashed_password = pbkdf2_sha256.hash(passwd)
            
            with self._get_connection() as con:
                con.execute(
                    "INSERT INTO users (login, passwd, mail) VALUES (?, ?, ?);",
                    (login, hashed_password, mail)
                )
                return True
        except sq.IntegrityError:
            return False

    def check_credentials(self, login: str, passwd: str) -> bool:

        """Проверяет логин и пароль (с верификацией хеша)"""

        with self._get_connection() as con:
            cursor = con.cursor()
            # Получаем хеш пароля из БД
            cursor.execute(
                "SELECT passwd FROM users WHERE login = ?;",
                (login,)
            )
            result = cursor.fetchone()
            
            if not result:  # Пользователь не найден
                return False
                
            stored_hash = result[0]
            # Сравниваем хеш введенного пароля с хранимым хешем
            return pbkdf2_sha256.verify(passwd, stored_hash)

    def update_login(self, old_login: str, new_login: str) -> bool:

        """Обновляет логин пользователя"""

        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users SET login = ? WHERE login = ?", 
                    (new_login, old_login)
                )
                return cursor.rowcount > 0
        except sq.IntegrityError:
            return False

    def update_password(self, login: str, new_passwd: str) -> bool:

        """Обновляет пароль пользователя (с хешированием)"""

        try:
            # Хешируем новый пароль
            hashed_password = pbkdf2_sha256.hash(new_passwd)
            
            with self._get_connection() as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users SET passwd = ? WHERE login = ?", 
                    (hashed_password, login)
                )
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    def update_email(self, login: str, new_mail: str) -> bool:

        """Обновляет email пользователя"""

        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users SET mail = ? WHERE login = ?", 
                    (new_mail, login)
                )
                return cursor.rowcount > 0
        except sq.IntegrityError:
            return False
        
    def register_for_course(self, login: str, course_titles: List[str]) -> None:
        """Регистрирует пользователя на курс и инициализирует прогресс по заданиям"""
        with self._get_connection() as con:
            cursor = con.cursor()
            
            # 1. Регистрируем пользователя на курсы
            course_records = [(login, title) for title in course_titles]
            cursor.executemany("""
                INSERT OR IGNORE INTO user_courses (user_login, course_title)
                VALUES (?, ?)
            """, course_records)
            
            # 2. Для каждого курса добавляем задания в прогресс
            for course_title in course_titles:
                # Получаем все задания курса
                cursor.execute("""
                    SELECT title FROM tasks 
                    WHERE course_title = ?
                """, (course_title,))
                tasks = [row[0] for row in cursor.fetchall()]
                
                # Создаем записи прогресса
                task_records = [(login, course_title, task_title) for task_title in tasks]
                cursor.executemany("""
                    INSERT OR IGNORE INTO task_progress (user_login, course_title, task_title)
                    VALUES (?, ?, ?)
                """, task_records)
            
            con.commit()
        
    def get_user(self, login: str) -> Optional[Tuple]:

        """Возвращает данные пользователя по логину"""

        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE login = ?", 
                (login,)
            )
            return cursor.fetchone()

    def get_all_users(self) -> List[Tuple]:

        """Возвращает список всех пользователей"""

        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()

    # ===== Методы для работы с курсами =====
    def add_course(self, title: str, owner_login: str, description: Optional[str] = None) -> bool:

        """Добавляет новый курс"""

        with self._get_connection() as con:
            cursor = con.cursor()
            
            # Проверяем существование пользователя с таким логином
            cursor.execute("SELECT 1 FROM users WHERE login = ?;", (owner_login,))
            if not cursor.fetchone():
                return False
                
            try:
                # Вставляем курс напрямую с логином владельца
                cursor.execute(
                    "INSERT INTO courses (title, description, owner_login) VALUES (?, ?, ?);",
                    (title, description, owner_login)
                )
                con.commit()  # Явное подтверждение изменений
                return True
            except sq.IntegrityError:
                return False

    def delete_course(self, course_title: str) -> bool:

        """Деактивирует курс"""

        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                UPDATE courses SET is_active = FALSE WHERE course_title = ?;
            """, (course_title,))
            return cursor.rowcount > 0

    def update_course(self, course_title: str, **kwargs) -> bool:

        """Обновляет информацию о курсе"""

        allowed_fields = {'title', 'description', 'owner_login', 'is_active'}
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
            
        params.append(course_title)
        
        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                query = f"""
                UPDATE courses 
                SET {', '.join(updates)} 
                WHERE course_title = ?;
                """
                cursor.execute(query, params)
                return cursor.rowcount > 0
        except sq.IntegrityError as e:
            print(f"Ошибка при обновлении курса: {e}")
            return False

    def get_course(self, course_title: str) -> Optional[Dict]:

        """Возвращает данные курса по ID"""

        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT title, description, owner_login, created_at, is_active FROM courses WHERE title = ?;
            """, (course_title,))
            row = cursor.fetchone()
            
            if row is None:
                return None
                
            return {
                'title': row[0],
                'description': row[1],
                'owner_login': row[2],
                'created_at': row[3],
                'is_active': bool(row[4])
            }

    def get_all_courses(self, active_only: bool = True) -> List[Dict]:

        """Возвращает список всех курсов"""

        with self._get_connection() as con:
            cursor = con.cursor()
            if active_only:
                cursor.execute("""
                    SELECT title, description, owner_login, created_at FROM courses WHERE is_active = TRUE;
                """)
            else:
                cursor.execute("""
                    SELECT title, description, owner_login, created_at, is_active FROM courses;
                """)
            
            return [{
                'title': row[0],
                'description': row[1],
                'owner_login': row[2],
                'created_at': row[3],
                'is_active': bool(row[4]) if not active_only else True
            } for row in cursor.fetchall()]

    # ===== Методы для работы с заданиями =====

    def mark_task_completed(self, user_login: str, course_title: str, 
                        task_title: str) -> None:
        """Отмечает задание как выполненное"""
        with self._get_connection() as con:
            con.execute("""
                UPDATE task_progress
                SET is_completed = TRUE
                WHERE user_login = ? 
                    AND course_title = ? 
                    AND task_title = ?
            """, (user_login, course_title, task_title))
            con.commit()

    def add_task_requirements(self, course_title: str, task_title: str, 
                            ban: list[str], demand: list[str]) -> None:
        """
        Добавляет требования к конкретному заданию
        
        :param course_title: Название курса
        :param task_title: Название задания
        :param ban: Список запрещенных элементов
        :param demand: Список обязательных элементов
        """
        # Сериализуем требования в JSON
        requirements = json.dumps({
            "ban": ban,
            "demand": demand
        })
        
        with self._get_connection() as con:
            con.execute("""
                UPDATE tasks
                SET requirements = ?
                WHERE course_title = ? AND title = ?
            """, (requirements, course_title, task_title))
            
            if con.total_changes == 0:
                raise ValueError("Задание не найдено")
            
            con.commit()

    def get_task_requirements(self, course_title: str, task_title: str) -> tuple[list[str], list[str]]:
        """
        Возвращает требования задания
        
        :param course_title: Название курса
        :param task_title: Название задания
        :return: (ban_list, demand_list)
        """
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT requirements
                FROM tasks
                WHERE course_title = ? AND title = ?
            """, (course_title, task_title))
            
            row = cursor.fetchone()
            
            if row and row[0]:
                data = json.loads(row[0])
                return data.get("ban", []), data.get("demand", [])
            
            return [], []  # Возвращаем пустые списки по умолчанию

    def add_task(self, course_title: str, task_title: str, 
                input_data: str, output_data: str,
                description: Optional[str] = None) -> bool:
        
        """Добавляет новое задание в курс"""
        
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("SELECT title FROM courses WHERE title = ?;", (course_title,))
            course = cursor.fetchone()
            
            if not course:
                return False
                
            try:
                con.execute(
                    """INSERT INTO tasks 
                    (course_title, title, description, input_data, output_data)
                    VALUES (?, ?, ?, ?, ?);""",
                    (course[0], task_title, description, input_data, output_data)
                )
                return True
            except sq.IntegrityError:
                return False

    def get_course_tasks(self, course_title: str) -> List[Dict]:
        """Возвращает все задания курса"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT title, description, input_data, output_data, requirements 
                FROM tasks
                WHERE course_title = ?;
            """, (course_title,))
            
            return [{
                'title': row[0],
                
                'description': row[1],
                'input': row[2],
                'output': row[3],
                'requirements ': row[4]
            } for row in cursor.fetchall()]

    def delete_task(self, task_title: str) -> bool:
        """Удаляет задание по ID"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM tasks WHERE title = ?;", (task_title,))
            con.commit()
            return cursor.rowcount > 0

    def update_task(self, task_title: int, **kwargs) -> bool:
        """Обновляет данные задания"""
        allowed_fields = {'title', 'description', 'input_data', 'output_data', 'requirements'}
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
            
        params.append(task_title)
        
        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                query = f"""
                UPDATE tasks 
                SET {', '.join(updates)} 
                WHERE task_title = ?;
                """
                cursor.execute(query, params)
                con.commit()
                return cursor.rowcount > 0
        except sq.Error as e:
            print(f"Ошибка при обновлении задания: {e}")
            return False

    # def get_task(self, task_title: int) -> Optional[Dict]:
    #     """Возвращает задание по названию"""
    #     with self._get_connection() as con:
    #         cursor = con.cursor()
    #         cursor.execute("""
    #             SELECT task_title, course_title, title as course_title, 
    #                    title, description, input_data, output_data
    #             FROM tasks
    #             WHERE task_title = ?;
    #         """, (task_title,))
    #         row = cursor.fetchone()
            
    #         if row is None:
    #             return None
                
    #         return {
    #             'task_title': row[0],
    #             'course_title': row[1],
    #             'course_title': row[2],
    #             'title': row[3],
    #             'description': row[4],
    #             'input_data': row[5],
    #             'output_data': row[6]
    #         }

data = EducationDB()
# data.update_password("alex", "12345")
# data.add_user("alex","1234", "1234@mail.com")
# # data.add_course("c++","alex", "a;lsdkfjl;askjdf")
# # data.add_task("c","sum","1 2 3","6","a;lskdfjlaskdj;f")
# print(data.check_credentials("alex","123456"))

# data.add_user("student1", "qwerty", "student1@mail.com")
# data.add_user("teacher1", "12345", "teacher1@mail.com")
# data.add_course("algosy", "teacher1", "teacher1")
# data.add_course("python", "teacher1")
# data.register_for_course('student1', ["algosy","python"])
# data.add_task("algosy", "sum", "1 2 3", "6")
# data.add_task_requirements("algosy", "sum", ["if","while"], ["for"])
# print(data.get_all_courses())
# print(data.get_course_tasks("algosy"))
# data.mark_task_completed("student1","algosy","sum")