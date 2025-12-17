# tests/test_app.py
import pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_app_creation():
    """Тест создания приложения"""
    from app import app
    assert app is not None
    assert app.name == 'app'

def test_security_headers():
    """Тест security headers"""
    from app import app
    
    with app.test_client() as client:
        response = client.get('/')
        
        # Проверяем security headers
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert 'Content-Security-Policy' in response.headers

def test_no_debug_in_production():
    """Тест что debug выключен при FLASK_ENV=production"""
    import app
    
    # Сохраняем оригинальное значение
    original_env = os.getenv('FLASK_ENV')
    
    # Устанавливаем production
    os.environ['FLASK_ENV'] = 'production'
    
    # Перезагружаем модуль
    import importlib
    importlib.reload(app)
    
    # Проверяем что debug=False
    assert not app.app.debug
    
    # Восстанавливаем
    if original_env:
        os.environ['FLASK_ENV'] = original_env
    else:
        del os.environ['FLASK_ENV']
    importlib.reload(app)

def test_sql_injection_protection():
    """Тест защиты от SQL-инъекций"""
    # Импортируем здесь чтобы не мешать другим тестам
    import re
    
    # Проверяем файлы на опасные паттерны
    dangerous_patterns = [
        r'f["\']SELECT',
        r'f["\']INSERT',
        r'f["\']UPDATE',
        r'f["\']DELETE',
        r'cursor\.execute.*f["\']',
        r'\+\s*["\'].*SELECT',
        r'%s.*SELECT'
    ]
    
    # Проверяем основные файлы проекта
    project_files = ['app.py', 'models.py', 'forms.py']
    
    for file in project_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        pytest.fail(f"Обнаружен опасный паттерн в {file}: {pattern}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])