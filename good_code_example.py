# good_code_example.py
# Пример безопасного кода

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

# БЕЗОПАСНО: debug режим только для разработки
DEBUG = os.getenv('FLASK_ENV') == 'development'

# БЕЗОПАСНО: секретный ключ из переменных окружения
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key-only-for-dev')

# БЕЗОПАСНО: параметризованные SQL запросы
def safe_login(username, password):
    """Безопасная функция аутентификации"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Безопасно: параметризованный запрос
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    
    result = cursor.fetchone()
    conn.close()
    return result

# БЕЗОПАСНО: валидация пользовательского ввода
def safe_execute(user_input):
    """Безопасная обработка пользовательского ввода"""
    # Валидация входных данных
    if not user_input.isalnum():
        raise ValueError("Некорректный ввод")
    
    # Безопасное использование
    print(f"Пользователь ввёл: {user_input}")

# БЕЗОПАСНО: пароли в переменных окружения
DATABASE_PASSWORD = os.getenv('DB_PASSWORD')

# БЕЗОПАСНО: современное хэширование
def safe_hash_password(password):
    """Безопасное хэширование пароля"""
    return generate_password_hash(password)

if __name__ == "__main__":
    print("Этот код соответствует best practices безопасности.")