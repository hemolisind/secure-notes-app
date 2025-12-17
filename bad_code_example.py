# bad_code_example.py
# Этот файл содержит уязвимости для тестирования CI/CD pipeline

import sqlite3
import os

DEBUG = False
# КРИТИЧЕСКАЯ УЯЗВИМОСТЬ 2: слабый секретный ключ
SECRET_KEY = 'simple-password-123'  # Слишком простой

# КРИТИЧЕСКАЯ УЯЗВИМОСТЬ 3: SQL-инъекция через конкатенацию строк
def vulnerable_login(username, password):
    """Уязвимая функция с SQL-инъекцией"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # ОПАСНО: конкатенация строк
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return result

# УЯЗВИМОСТЬ 4: выполнение shell команд из пользовательского ввода
def execute_command(user_input):
    """Опасная функция с выполнением shell команд"""
    os.system(f"echo {user_input}")

# УЯЗВИМОСТЬ 5: хардкод credentials
DATABASE_PASSWORD = "admin123"  # Пароли не должны быть в коде

# УЯЗВИМОСТЬ 6: использование устаревших/небезопасных модулей
import md5  # Устаревший и небезопасный

def hash_password(password):
    """Небезопасное хэширование пароля"""
    return md5.new(password).hexdigest()  # MD5 легко взламывается

if __name__ == "__main__":
    print("Этот код содержит критические уязвимости безопасности")
    print("CI/CD pipeline должен его заблокировать.")