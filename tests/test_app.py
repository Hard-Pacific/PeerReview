from src.app import app
import pytest

class TestWebApp:
    
    def test_get(self):
        # Отправка GET запроса
        response = app.test_client().get('/')
        # Проверяем, что рендерится шаблон
        assert response.status_code == 200