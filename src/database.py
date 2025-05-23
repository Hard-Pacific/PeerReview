# import sqlite3 as sq
# from typing import Optional, Tuple, List, Dict

# class UsersDB:
#     def __init__(self, db_name: str = "users.db"):
#         self.db_name = db_name
#         self._initialize_database()

#     def _initialize_database(self):
#         """Инициализирует базу данных и создает таблицы при необходимости"""
#         with self._get_connection() as con:
#             con.execute(
#                 """
#                 CREATE TABLE IF NOT EXISTS students (
#                     user_id INTEGER NOT NULL,
#                     login TEXT UNIQUE NOT NULL,
#                     mail TEXT UNIQUE NOT NULL,
#                     passwd TEXT NOT NULL
#                 );
#                 """
#             )

#     def _get_connection(self):
#         """Возвращает соединение с базой данных"""
#         return sq.connect(self.db_name)

#     def add_student(self, login: str, passwd: str, mail: str) -> bool:
#         """Добавляет нового студента в базу данных"""
#         try:
#             with self._get_connection() as con:
#                 con.execute(
#                     "INSERT INTO students VALUES (?, ?, ?);", 
#                     (login, mail, passwd)
#                 )
#                 return True
#         except sq.IntegrityError:
#             # Логин или почта уже существуют
#             return False

#     def delete_student(self, login: str) -> bool:
#         """Удаляет студента по логину"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute(
#                 "DELETE FROM students WHERE login = ?", 
#                 (login,)
#             )
#             return cursor.rowcount > 0

#     def update_login(self, old_login: str, new_login: str) -> bool:
#         """Обновляет логин студента"""
#         try:
#             with self._get_connection() as con:
#                 cursor = con.cursor()
#                 cursor.execute(
#                     "UPDATE students SET login = ? WHERE login = ?", 
#                     (new_login, old_login)
#                 )
#                 return cursor.rowcount > 0
#         except sq.IntegrityError:
#             # Новый логин уже занят
#             return False

#     def update_password(self, login: str, new_passwd: str) -> bool:
#         """Обновляет пароль студента по логину"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute(
#                 "UPDATE students SET passwd = ? WHERE login = ?", 
#                 (new_passwd, login)
#             )
#             return cursor.rowcount > 0

#     def update_email(self, login: str, new_mail: str) -> bool:
#         """Обновляет email студента по логину"""
#         try:
#             with self._get_connection() as con:
#                 cursor = con.cursor()
#                 cursor.execute(
#                     "UPDATE students SET mail = ? WHERE login = ?", 
#                     (new_mail, login)
#                 )
#                 return cursor.rowcount > 0
#         except sq.IntegrityError:
#             # Новый email уже занят
#             return False

#     def check_credentials(self, login: str, passwd: str) -> bool:
#         """Проверяет правильность логина и пароля"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute(
#                 "SELECT 1 FROM students WHERE login = ? AND passwd = ?", 
#                 (login, passwd)
#             )
#             return cursor.fetchone() is not None

#     def get_student(self, login: str) -> Optional[Tuple]:
#         """Возвращает данные студента по логину"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute(
#                 "SELECT * FROM students WHERE login = ?", 
#                 (login,)
#             )
#             return cursor.fetchone()

#     def get_all_students(self) -> List[Tuple]:
#         """Возвращает список всех студентов"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute("SELECT * FROM students")
#             return cursor.fetchall()
        
#     # def fetch_students(self):
#     #     con = sq.connect("data.db")
#     #     cursor = con.cursor()
#     #     cursor.execute("SELECT * FROM students")
#     #     return cursor.fetchall()

# class CoursesDB:
#     def __init__(self, db_name: str = "courses.db"):
#         """Инициализация базы данных курсов"""
#         self.db_name = db_name
#         self._initialize_database()

#     def _initialize_database(self):
#         """Инициализирует базу данных и создает таблицы"""
#         with self._get_connection() as con:
#             con.execute("""
#                 CREATE TABLE IF NOT EXISTS courses (
#                     course_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     title TEXT NOT NULL,
#                     description TEXT,
#                     owner_id INTEGER NOT NULL,
#                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     is_active BOOLEAN DEFAULT TRUE,
#                     FOREIGN KEY (owner_id) REFERENCES users(user_id)
#                 );
#             """)
#             # Индексы для быстрого поиска
#             con.execute("CREATE INDEX IF NOT EXISTS idx_courses_owner ON courses(owner_id);")
#             con.execute("CREATE INDEX IF NOT EXISTS idx_courses_active ON courses(is_active);")

#     def _get_connection(self):
#         """Возвращает соединение с базой данных"""
#         return sq.connect(self.db_name)

#     def add_course(self, title: str, owner_id: int, description: Optional[str] = None) -> bool:
#         """Добавляет новый курс в базу данных"""
#         try:
#             with self._get_connection() as con:
#                 con.execute("""
#                     INSERT INTO courses (title, description, owner_id)
#                     VALUES (?, ?, ?);
#                 """, (title, description, owner_id))
#                 return True
#         except sq.IntegrityError as e:
#             print(f"Ошибка при добавлении курса: {e}")
#             return False

#     def delete_course(self, course_id: int) -> bool:
#         """Удаляет курс по ID (мягкое удаление - деактивация)"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute("""
#                 UPDATE courses SET is_active = FALSE WHERE course_id = ?;
#             """, (course_id,))
#             return cursor.rowcount > 0

#     def update_course(self, course_id: int, **kwargs) -> bool:
#         """Обновляет информацию о курсе"""
#         allowed_fields = {'title', 'description', 'owner_id', 'is_active'}
#         updates = []
#         params = []
        
#         for field, value in kwargs.items():
#             if field in allowed_fields:
#                 updates.append(f"{field} = ?")
#                 params.append(value)
        
#         if not updates:
#             return False
            
#         params.append(course_id)
        
#         try:
#             with self._get_connection() as con:
#                 cursor = con.cursor()
#                 query = f"""
#                 UPDATE courses 
#                 SET {', '.join(updates)} 
#                 WHERE course_id = ?;
#                 """
#                 cursor.execute(query, params)
#                 return cursor.rowcount > 0
#         except sq.IntegrityError as e:
#             print(f"Ошибка при обновлении курса: {e}")
#             return False

#     def get_course(self, course_id: int) -> Optional[Dict]:
#         """Возвращает данные курса по ID"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute("""
#                 SELECT course_id, title, description, owner_id, created_at, is_active
#                 FROM courses
#                 WHERE course_id = ?;
#             """, (course_id,))
#             row = cursor.fetchone()
            
#             if row is None:
#                 return None
                
#             return {
#                 'course_id': row[0],
#                 'title': row[1],
#                 'description': row[2],
#                 'owner_id': row[3],
#                 'created_at': row[4],
#                 'is_active': bool(row[5])
#             }

#     def get_all_courses(self, active_only: bool = True) -> List[Dict]:
#         """Возвращает список всех курсов"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             if active_only:
#                 cursor.execute("""
#                     SELECT course_id, title, description, owner_id, created_at
#                     FROM courses
#                     WHERE is_active = TRUE;
#                 """)
#             else:
#                 cursor.execute("""
#                     SELECT course_id, title, description, owner_id, created_at, is_active
#                     FROM courses;
#                 """)
            
#             return [{
#                 'course_id': row[0],
#                 'title': row[1],
#                 'description': row[2],
#                 'owner_id': row[3],
#                 'created_at': row[4],
#                 'is_active': bool(row[5]) if not active_only else True
#             } for row in cursor.fetchall()]

#     def get_user_courses(self, owner_id: int, active_only: bool = True) -> List[Dict]:
#         """Возвращает курсы, принадлежащие конкретному пользователю"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             if active_only:
#                 cursor.execute("""
#                     SELECT course_id, title, description, created_at
#                     FROM courses
#                     WHERE owner_id = ? AND is_active = TRUE;
#                 """, (owner_id,))
#             else:
#                 cursor.execute("""
#                     SELECT course_id, title, description, created_at, is_active
#                     FROM courses
#                     WHERE owner_id = ?;
#                 """, (owner_id,))
            
#             return [{
#                 'course_id': row[0],
#                 'title': row[1],
#                 'description': row[2],
#                 'created_at': row[3],
#                 'is_active': bool(row[4]) if not active_only else True
#             } for row in cursor.fetchall()]

#     def search_courses(self, search_term: str) -> List[Dict]:
#         """Поиск курсов по названию или описанию"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             search_pattern = f"%{search_term}%"
#             cursor.execute("""
#                 SELECT course_id, title, description, owner_id, created_at
#                 FROM courses
#                 WHERE (title LIKE ? OR description LIKE ?) AND is_active = TRUE;
#             """, (search_pattern, search_pattern))
            
#             return [{
#                 'course_id': row[0],
#                 'title': row[1],
#                 'description': row[2],
#                 'owner_id': row[3],
#                 'created_at': row[4]
#             } for row in cursor.fetchall()]
        
# class TasksDB:
#     def __init__(self, db_name: str = "courses.db"):
#         """Инициализация базы данных заданий"""
#         self.db_name = db_name
#         self._initialize_database()

#     def _initialize_database(self):
#         """Создает таблицу заданий, если она не существует"""
#         with self._get_connection() as con:
#             con.execute("""
#                 CREATE TABLE IF NOT EXISTS tasks (
#                     task_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     course_id INTEGER NOT NULL,
#                     title TEXT NOT NULL,
#                     description TEXT,
#                     input_description TEXT,
#                     output_description TEXT,
#                     FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
#                 );
#             """)
#             con.execute("CREATE INDEX IF NOT EXISTS idx_tasks_course ON tasks(course_id);")

#     def _get_connection(self):
#         """Возвращает соединение с базой данных"""
#         return sq.connect(self.db_name)

#     def add_task(self, course_id: int, title: str, 
#                 description: Optional[str] = None,
#                 input_desc: Optional[str] = None,
#                 output_desc: Optional[str] = None) -> bool:
#         """Добавляет новое задание в курс"""
#         try:
#             with self._get_connection() as con:
#                 con.execute("""
#                     INSERT INTO tasks (course_id, title, description, input_description, output_description)
#                     VALUES (?, ?, ?, ?, ?);
#                 """, (course_id, title, description, input_desc, output_desc))
#                 return True
#         except sq.IntegrityError as e:
#             print(f"Ошибка при добавлении задания: {e}")
#             return False

#     def delete_task(self, task_id: int) -> bool:
#         """Удаляет задание по ID"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute("DELETE FROM tasks WHERE task_id = ?;", (task_id,))
#             con.commit()
#             return cursor.rowcount > 0

#     def update_task(self, task_id: int, **kwargs) -> bool:
#         """Обновляет данные задания"""
#         allowed_fields = {'title', 'description', 'input_description', 'output_description'}
#         updates = []
#         params = []
        
#         for field, value in kwargs.items():
#             if field in allowed_fields:
#                 updates.append(f"{field} = ?")
#                 params.append(value)
        
#         if not updates:
#             return False
            
#         params.append(task_id)
        
#         try:
#             with self._get_connection() as con:
#                 cursor = con.cursor()
#                 query = f"""
#                 UPDATE tasks 
#                 SET {', '.join(updates)} 
#                 WHERE task_id = ?;
#                 """
#                 cursor.execute(query, params)
#                 con.commit()
#                 return cursor.rowcount > 0
#         except sq.Error as e:
#             print(f"Ошибка при обновлении задания: {e}")
#             return False

#     def get_task(self, task_id: int) -> Optional[Dict]:
#         """Возвращает задание по ID"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute("""
#                 SELECT t.task_id, t.course_id, c.title as course_title, 
#                        t.title, t.description, t.input_description, t.output_description
#                 FROM tasks t
#                 JOIN courses c ON t.course_id = c.course_id
#                 WHERE t.task_id = ?;
#             """, (task_id,))
#             row = cursor.fetchone()
            
#             if row is None:
#                 return None
                
#             return {
#                 'task_id': row[0],
#                 'course_id': row[1],
#                 'course_title': row[2],
#                 'title': row[3],
#                 'description': row[4],
#                 'input_description': row[5],
#                 'output_description': row[6]
#             }

#     def get_course_tasks(self, course_id: int) -> List[Dict]:
#         """Возвращает все задания курса"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             cursor.execute("""
#                 SELECT task_id, title, description, input_description, output_description
#                 FROM tasks
#                 WHERE course_id = ?;
#             """, (course_id,))
            
#             return [{
#                 'task_id': row[0],
#                 'title': row[1],
#                 'description': row[2],
#                 'input_description': row[3],
#                 'output_description': row[4]
#             } for row in cursor.fetchall()]

#     def search_tasks(self, course_id: int, search_term: str) -> List[Dict]:
#         """Ищет задания в курсе по названию или описанию"""
#         with self._get_connection() as con:
#             cursor = con.cursor()
#             search_pattern = f"%{search_term}%"
#             cursor.execute("""
#                 SELECT task_id, title, description
#                 FROM tasks
#                 WHERE course_id = ? AND (title LIKE ? OR description LIKE ?);
#             """, (course_id, search_pattern, search_pattern))
            
#             return [{
#                 'task_id': row[0],
#                 'title': row[1],
#                 'description': row[2]
#             } for row in cursor.fetchall()]




# users = UsersDB()
# courses = CoursesDB()
# # courses.add_course("С++", 1, "дфжвыла")
# tasks = TasksDB()
# tasks.add_task(1, "сумма чисел", "написать жфдывлаождфыова", "1 2", "3")

# # data.add_student('alex', '234', '234234234')
# # data.replace_login('alex', 'alexander')
# # print(users.check_credentials('Alexander', '234'))
# # data.delete_student('alex')

import sqlite3 as sq
from typing import Optional, List, Dict, Tuple

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
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT UNIQUE NOT NULL,
                    mail TEXT UNIQUE NOT NULL,
                    passwd TEXT NOT NULL
                );
            """)

            # Таблица курсов
            con.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    owner_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (owner_id) REFERENCES users(user_id)
                );
            """)

            # Таблица заданий
            con.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
                );
            """)

            # Создаем индексы
            con.execute("CREATE INDEX IF NOT EXISTS idx_users_login ON users(login);")
            con.execute("CREATE INDEX IF NOT EXISTS idx_courses_owner ON courses(owner_id);")
            con.execute("CREATE INDEX IF NOT EXISTS idx_tasks_course ON tasks(course_id);")

    def _get_connection(self):
        """Возвращает соединение с базой данных"""
        return sq.connect(self.db_name)

    # ===== Методы для работы с пользователями =====
    def add_user(self, login: str, passwd: str, mail: str) -> bool:
        """Добавляет нового пользователя"""
        try:
            with self._get_connection() as con:
                con.execute(
                    "INSERT INTO users (login, passwd, mail) VALUES (?, ?, ?);",
                    (login, passwd, mail)
                )
                return True
        except sq.IntegrityError:
            return False

    def check_credentials(self, login: str, passwd: str) -> bool:
        """Проверяет логин и пароль"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE login = ? AND passwd = ?;",
                (login, passwd)
            )
            return cursor.fetchone() is not None

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
        """Обновляет пароль пользователя"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                "UPDATE users SET passwd = ? WHERE login = ?", 
                (new_passwd, login)
            )
            return cursor.rowcount > 0

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
            cursor.execute("SELECT user_id FROM users WHERE login = ?;", (owner_login,))
            owner = cursor.fetchone()
            
            if not owner:
                return False
                
            try:
                con.execute(
                    "INSERT INTO courses (title, description, owner_id) VALUES (?, ?, ?);",
                    (title, description, owner[0])
                )
                return True
            except sq.IntegrityError:
                return False

    def delete_course(self, course_id: int) -> bool:
        """Деактивирует курс"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                UPDATE courses SET is_active = FALSE WHERE course_id = ?;
            """, (course_id,))
            return cursor.rowcount > 0

    def update_course(self, course_id: int, **kwargs) -> bool:
        """Обновляет информацию о курсе"""
        allowed_fields = {'title', 'description', 'owner_id', 'is_active'}
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
            
        params.append(course_id)
        
        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                query = f"""
                UPDATE courses 
                SET {', '.join(updates)} 
                WHERE course_id = ?;
                """
                cursor.execute(query, params)
                return cursor.rowcount > 0
        except sq.IntegrityError as e:
            print(f"Ошибка при обновлении курса: {e}")
            return False

    def get_course(self, course_id: int) -> Optional[Dict]:
        """Возвращает данные курса по ID"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT course_id, title, description, owner_id, created_at, is_active
                FROM courses
                WHERE course_id = ?;
            """, (course_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
                
            return {
                'course_id': row[0],
                'title': row[1],
                'description': row[2],
                'owner_id': row[3],
                'created_at': row[4],
                'is_active': bool(row[5])
            }

    def get_all_courses(self, active_only: bool = True) -> List[Dict]:
        """Возвращает список всех курсов"""
        with self._get_connection() as con:
            cursor = con.cursor()
            if active_only:
                cursor.execute("""
                    SELECT course_id, title, description, owner_id, created_at
                    FROM courses
                    WHERE is_active = TRUE;
                """)
            else:
                cursor.execute("""
                    SELECT course_id, title, description, owner_id, created_at, is_active
                    FROM courses;
                """)
            
            return [{
                'course_id': row[0],
                'title': row[1],
                'description': row[2],
                'owner_id': row[3],
                'created_at': row[4],
                'is_active': bool(row[5]) if not active_only else True
            } for row in cursor.fetchall()]

    # ===== Методы для работы с заданиями =====
    def add_task(self, course_title: str, task_title: str, 
                input_data: str, output_data: str,
                description: Optional[str] = None) -> bool:
        """Добавляет новое задание в курс"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("SELECT course_id FROM courses WHERE title = ?;", (course_title,))
            course = cursor.fetchone()
            
            if not course:
                return False
                
            try:
                con.execute(
                    """INSERT INTO tasks 
                    (course_id, title, description, input_data, output_data)
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
                SELECT t.task_id, t.title, t.description, t.input_data, t.output_data
                FROM tasks t
                JOIN courses c ON t.course_id = c.course_id
                WHERE c.title = ?;
            """, (course_title,))
            
            return [{
                'task_id': row[0],
                'title': row[1],
                'description': row[2],
                'input': row[3],
                'output': row[4]
            } for row in cursor.fetchall()]

    def delete_task(self, task_id: int) -> bool:
        """Удаляет задание по ID"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM tasks WHERE task_id = ?;", (task_id,))
            con.commit()
            return cursor.rowcount > 0

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновляет данные задания"""
        allowed_fields = {'title', 'description', 'input_data', 'output_data'}
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
            
        params.append(task_id)
        
        try:
            with self._get_connection() as con:
                cursor = con.cursor()
                query = f"""
                UPDATE tasks 
                SET {', '.join(updates)} 
                WHERE task_id = ?;
                """
                cursor.execute(query, params)
                con.commit()
                return cursor.rowcount > 0
        except sq.Error as e:
            print(f"Ошибка при обновлении задания: {e}")
            return False

    def get_task(self, task_id: int) -> Optional[Dict]:
        """Возвращает задание по ID"""
        with self._get_connection() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT t.task_id, t.course_id, c.title as course_title, 
                       t.title, t.description, t.input_data, t.output_data
                FROM tasks t
                JOIN courses c ON t.course_id = c.course_id
                WHERE t.task_id = ?;
            """, (task_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
                
            return {
                'task_id': row[0],
                'course_id': row[1],
                'course_title': row[2],
                'title': row[3],
                'description': row[4],
                'input_data': row[5],
                'output_data': row[6]
            }

data = EducationDB()
data.add_user("alex", 1234, "1234@mail.com")
data.add_course("c++","alex", "a;lsdkfjl;askjdf")
data.add_task("c","sum","1 2 3","6","a;lskdfjlaskdj;f")