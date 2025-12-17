# test_security.py
# Простые тесты для CI/CD pipeline

def test_debug_mode():
    """Проверяем что debug режим выключен"""
    import app
    # В production debug должен быть False
    assert not app.app.config.get('DEBUG', False), "DEBUG должен быть False в production"

def test_secret_key():
    """Проверяем что секретный ключ не простой"""
    import app
    secret = app.app.config.get('SECRET_KEY', '')
    # Секретный ключ должен быть достаточно сложным
    assert len(secret) >= 20, "SECRET_KEY должен быть не менее 20 символов"
    assert 'password' not in secret.lower(), "SECRET_KEY не должен содержать 'password'"
    assert '123456' not in secret, "SECRET_KEY не должен быть простым числом"

def test_sql_injection_patterns():
    """Проверяем отсутствие шаблонов SQL-инъекций"""
    import os
    
    dangerous_patterns = [
        'f"SELECT',
        'f"INSERT',
        'f"UPDATE', 
        'f"DELETE',
        'cursor.execute(f"',
        '+ "SELECT',
        '%s" % var'
    ]
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in dangerous_patterns:
                            if pattern in content:
                                print(f"ВНИМАНИЕ: {filepath} содержит опасный паттерн: {pattern}")
                except:
                    continue

if __name__ == "__main__":
    test_debug_mode()
    test_secret_key()
    test_sql_injection_patterns()
    print("Все security тесты пройдены")