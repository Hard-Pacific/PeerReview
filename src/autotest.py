import pytest
import subprocess
import sys
from pathlib import Path
from typing import Dict

class StudentProgramTester:
    def __init__(self, work_dir: str = "C:/Users/kirus/PeerReview-1/uploads"):
        self.work_dir = Path(work_dir)
    
    def _run_program(self, student_file: Path, input_data: str) -> str:
        """Приватный метод для запуска программы студента"""
        try:
            result = subprocess.run(
                [sys.executable, str(student_file)],
                input=input_data,
                text=True,
                capture_output=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Ошибка выполнения: {e.stderr.strip()}"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def test_single_program(self, student_file: Path, test_cases: Dict[str, str]) -> bool:
        """Тестирует одну программу и возвращает результат"""
        return all(
            self._run_program(student_file, input_data) == expected_output
            for input_data, expected_output in test_cases.items()
        )
    
    def test_all_programs(self, test_cases: Dict[str, str]) -> Dict[str, str]:
        """Тестирует все программы и возвращает словарь результатов"""
        return {
            file.name: "true" if self.test_single_program(file, test_cases) else "false"
            for file in self.work_dir.glob("*.py")
        }


# Фикстура pytest для создания тестового экземпляра
@pytest.fixture
def tester():
    return StudentProgramTester()

