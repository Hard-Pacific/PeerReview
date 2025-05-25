import sqlite3 as sq
from typing import Optional, List, Dict, Tuple
from passlib.hash import pbkdf2_sha256

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
data.update_password("alex", "12345")
data.add_user("alex","1234", "1234@mail.com")
# data.add_course("c++","alex", "a;lsdkfjl;askjdf")
# data.add_task("c","sum","1 2 3","6","a;lskdfjlaskdj;f")
print(data.check_credentials("alex","123456"))