import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import os


class AutoTest:
    """Универсальный тестер для программ с вводом/выводом и только выводом"""
    
    LANGUAGE_CONFIG = {
        'python': {
            'command': ['python', '{file}'],
            'ext': '.py',
            'compile': None
        },
        'c': {
            'command': ['./{file_stem}'],
            'ext': '.c',
            'compile': ['gcc', '{file}', '-o', '{file_stem}']
        },
        'go': {
            'command': ['go', 'run', '{file}'],
            'ext': '.go',
            'compile': None
        },
        'rust': {
            'command': ['./{file_stem}'],
            'ext': '.rs',
            'compile': ['rustc', '{file}']
        }
    }

    def __init__(self, work_dir: str = "C:/Users/kirus/PeerReview-1/uploads"):
        self.work_dir = Path(work_dir)

    def _detect_language(self, file: Path) -> Optional[str]:
        """Определяет язык программирования по расширению файла"""
        for lang, config in self.LANGUAGE_CONFIG.items():
            if file.suffix == config['ext']:
                return lang
        return None

    def _compile_if_needed(self, file: Path, lang: str) -> bool:
        """Компилирует программу при необходимости"""
        compile_cmd = self.LANGUAGE_CONFIG[lang].get('compile')
        if not compile_cmd:
            return True
            
        cmd = [part.format(file=str(file), file_stem=file.stem) for part in compile_cmd]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Ошибка компиляции {file.name}: {e.stderr}")
            return False


    def _run_program(self, file: Path, lang: str, input_data: Optional[str] = None) -> str:
        """Запускает программу с опциональным вводом"""
        config = self.LANGUAGE_CONFIG[lang]
        cmd = [part.format(file=str(file), file_stem=file.stem) for part in config['command']]
        
        try:
            result = subprocess.run(
                cmd,
                input=input_data if input_data else None,  # None означает отсутствие ввода
                text=True,
                capture_output=True,
                timeout=5
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def test_program(self, file: Path, test_case: Optional[Dict[str, str]] = None, 
                   expected_output: Optional[str] = None) -> str:
        """
        Универсальный метод тестирования:
        - С входными данными: test_case={"ввод": "ожидаемый вывод"}
        - Без входных данных: expected_output="ожидаемый вывод"
        """
        lang = self._detect_language(file)
        if not lang:
            return "UNSUPPORTED_LANGUAGE"
            
        if not self._compile_if_needed(file, lang):
            return "COMPILE_ERROR"
        
        if test_case:
            # Режим с входными данными
            for input_data, expected in test_case.items():
                actual = self._run_program(file, lang, input_data)
                if actual != expected:
                    return f"FAIL (input: '{input_data}', got: '{actual}')"
            return "True"
        elif expected_output is not None:
            # Режим только с выводом
            actual = self._run_program(file, lang)
            return "True" if actual == expected_output else f"False (got: '{actual}')"
        else:
            return "INVALID_TEST_CASE"

    def test_all(self, 
                test_case: Optional[Dict[str, str]] = None,
                expected_output: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """
        Тестирует все программы в директории:
        - Либо с входными данными (test_case)
        - Либо только проверкой вывода (expected_output)
        """
        results = {lang: {} for lang in self.LANGUAGE_CONFIG}
        
        for file in self.work_dir.iterdir():
            if not file.is_file():
                continue
                
            lang = self._detect_language(file)
            if not lang:
                continue
                
            result = self.test_program(file, test_case, expected_output)
            results[lang][file.name] = result
        
        return results
    

tester = AutoTest()

# print(tester.test_all({"2":"4","1":"1","3":"9"}))  # Проверка квадратов чисел
