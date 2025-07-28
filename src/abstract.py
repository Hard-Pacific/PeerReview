from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class Abstract(ABC):
    """
    Абстрактный класс, содержащий методы тестировщика(autotest.py) 
    и базы данных(database.py) и их описания
    """


# методы для работы с пользователями
    @abstractmethod
    def add_user(self, login: str, passwd: str, mail: str) -> bool:
        """Добавляет нового пользователя с хешированным паролем"""
        pass

    @abstractmethod
    def check_credentials(self, login: str, passwd: str) -> bool:
        """Проверяет логин и пароль (с верификацией хеша)"""
        pass

    @abstractmethod
    def update_login(self, old_login: str, new_login: str) -> bool:

        """Обновляет логин пользователя"""
        pass

    @abstractmethod
    def update_password(self, login: str, new_passwd: str) -> bool:
        """Обновляет пароль пользователя (с хешированием)"""
        pass

    @abstractmethod
    def update_email(self, login: str, new_mail: str) -> bool:
        """Обновляет email пользователя"""
        pass

    @abstractmethod
    def get_user(self, login: str) -> Optional[Tuple]:
        """Возвращает данные пользователя по логину"""
        pass

    @abstractmethod
    def get_all_users(self) -> List[Tuple]:
        """Возвращает список всех пользователей"""
        pass

# методы для работы с курсами
    @abstractmethod
    def add_course(self, title: str, owner_login: str, description: Optional[str] = None) -> bool:
        """Добавляет новый курс"""
        pass

    @abstractmethod
    def delete_course(self, course_id: int) -> bool:
        """Деактивирует курс"""
        pass

    @abstractmethod
    def update_course(self, course_id: int, **kwargs) -> bool:
        """Обновляет информацию о курсе"""
        pass

    @abstractmethod
    def get_course(self, course_id: int) -> Optional[Dict]:
        """Возвращает данные курса по ID"""
        pass

    @abstractmethod
    def get_all_courses(self, active_only: bool = True) -> List[Dict]:
        """Возвращает список всех курсов"""
        pass

# методы для работы с заданиями
    @abstractmethod
    def add_task(self, course_title: str, task_title: str, 
                input_data: str, output_data: str,
                description: Optional[str] = None) -> bool:
        """Добавляет новое задание в курс"""
        pass

    @abstractmethod
    def get_course_tasks(self, course_title: str) -> List[Dict]:
        """Возвращает все задания курса"""
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        """Удаляет задание по ID"""
        pass

    @abstractmethod
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновляет данные задания"""
        pass

    # @abstractmethod
    # def get_task(self, task_id: int) -> Optional[Dict]:
    #     """Возвращает задание по ID"""
    #     pass

    def add_task_requirements(self, course_title: str, task_title: str, 
                            ban: list[str], demand: list[str]) -> None:
        """
        Добавляет требования к конкретному заданию
        
        :param course_title: Название курса
        :param task_title: Название задания
        :param ban: Список запрещенных элементов
        :param demand: Список обязательных элементов
        """
        pass
    
    def get_task_requirements(self, course_title: str, task_title: str) -> tuple[list[str], list[str]]:
        """
        Возвращает требования задания
        
        :param course_title: Название курса
        :param task_title: Название задания
        :return: (ban_list, demand_list)
        """
        pass

# методы для работы с таблицей записанных на курсы пользователей
    def register_for_course(self, login: str, course_titles: List[str]) -> None:

        """Регистрирует пользователя на курс, сразу инициализирует выполнения всех заданий и выставляет значения на 0"""
        pass
# методы для работы с таблицей выполненных пользователем заданий
    def mark_task_completed(self, user_login: str, course_title: str, 
                        task_title: str) -> None:
        """Отмечает задание как выполненное"""
        pass

# методы для работы с тестировщиком
    @abstractmethod
    def test_program(self, file: Path, test_case: Optional[Dict[str, str]] = None, 
                   expected_output: Optional[str] = None) -> str:
        """
        Универсальный метод тестирования:
        - С входными данными: test_case={"ввод": "ожидаемый вывод"}
        - Без входных данных: expected_output="ожидаемый вывод"
        """
        pass

    @abstractmethod
    def test_all(self, 
                test_case: Optional[Dict[str, str]] = None,
                expected_output: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """
        Тестирует все программы в директории:
        - Либо с входными данными (test_case)
        - Либо только проверкой вывода (expected_output)
        """
        pass
    # отказаться от айди, поиск только по именам, логинам и тд, клонировать проект, 
    # добавления в базу данных бан и деманд из требований, метод, который записывает пользователя на курс(подумать как реализовать список заданий)
    # отметка сделанных студентом работ(доп)