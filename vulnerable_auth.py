import os
import sqlite3
from flask import Flask, request, redirect, url_for, flash, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key-only')

# Уязвимая функция аутентификации с SQL-инъекцией
def vulnerable_login(username, password):
    """УЯЗВИМАЯ функция входа - использует конкатенацию строк"""
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    # УЯЗВИМЫЙ запрос - конкатенация строк
    query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
    print(f"ВЫПОЛНЯЕТСЯ УЯЗВИМЫЙ ЗАПРОС: {query}")
    
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    return user

@app.route('/vulnerable_login', methods=['GET', 'POST'])
def vulnerable_login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = vulnerable_login(username, password)
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Успешный вход</title>
                <style>
                    body {{ font-family: Arial; margin: 40px; }}
                    .success {{ color: green; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>Уязвимая форма входа</h1>
                <div class="success">Успешный вход! Добро пожаловать, {user[1]}</div>
                <p>ID пользователя: {user[0]}</p>
                <br>
                <a href="/vulnerable_dashboard">Перейти в панель управления</a>
            </body>
            </html>
            '''
        else:
            error_html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Уязвимая форма входа</title>
                <style>
                    body { font-family: Arial; margin: 40px; }
                    form { max-width: 300px; }
                    input, button { width: 100%; padding: 8px; margin: 5px 0; }
                    .error { color: red; }
                </style>
            </head>
            <body>
                <h1>Уязвимая форма входа</h1>
                <p>Эта форма уязвима к SQL-инъекциям</p>
                
                <div class="error">Неверные учетные данные</div>
                
                <form method="POST">
                    <input type="text" name="username" placeholder="Имя пользователя" required>
                    <input type="password" name="password" placeholder="Пароль" required>
                    <button type="submit">Войти</button>
                </form>
                
                <p><strong>Пример SQL-инъекции:</strong></p>
                <p>Логин: <code>' OR '1'='1</code></p>
                <p>Пароль: <code>' OR '1'='1</code></p>
                
                <br>
                <a href="/">Назад к безопасной версии</a>
            </body>
            </html>
            '''
            return error_html
    
    # GET запрос - показать форму
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Уязвимая форма входа</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            form { max-width: 300px; }
            input, button { width: 100%; padding: 8px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>Уязвимая форма входа</h1>
        <p>Эта форма уязвима к SQL-инъекциям</p>
        
        <form method="POST">
            <input type="text" name="username" placeholder="Имя пользователя" required>
            <input type="password" name="password" placeholder="Пароль" required>
            <button type="submit">Войти</button>
        </form>
        
        <p><strong>Пример SQL-инъекции:</strong></p>
        <p>Логин: <code>' OR '1'='1</code></p>
        <p>Пароль: <code>' OR '1'='1</code></p>
        
        <br>
        <a href="/">Назад к безопасной версии</a>
    </body>
    </html>
    '''

@app.route('/vulnerable_dashboard')
def vulnerable_dashboard():
    if 'user_id' not in session:
        return redirect('/vulnerable_login')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Панель управления</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            .success {{ color: green; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Панель управления</h1>
        <div class="success">Успешный вход как: {session.get('username', 'Unknown')}</div>
        <p>ID пользователя: {session.get('user_id', 'Unknown')}</p>
        <br>
        <a href="/vulnerable_logout">Выйти</a> | 
        <a href="/">Безопасная версия</a>
    </body>
    </html>
    '''

@app.route('/vulnerable_logout')
def vulnerable_logout():
    session.clear()
    return redirect('/vulnerable_login')

if __name__ == '__main__':
    app.run(debug=True, port=5001)