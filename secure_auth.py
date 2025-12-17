import os
from flask import Flask, request, redirect, url_for, session
from dotenv import load_dotenv
from models import db, User
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key-only')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# БЕЗОПАСНАЯ функция аутентификации
def secure_login(username, password):
    """БЕЗОПАСНАЯ функция входа - использует параметризованные запросы SQLAlchemy"""
    # Безопасный запрос через ORM
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        return user
    return None

@app.route('/secure_login', methods=['GET', 'POST'])
def secure_login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = secure_login(username, password)
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Безопасный вход</title>
                <style>
                    body {{ font-family: Arial; margin: 40px; }}
                    .success {{ color: green; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>Безопасная форма входа</h1>
                <div class="success">Успешный вход! Добро пожаловать, {user.username}</div>
                <p>ID пользователя: {user.id}</p>
                <p>Используется безопасный параметризованный запрос</p>
                <br>
                <a href="/secure_dashboard">Перейти в панель управления</a>
            </body>
            </html>
            '''
        else:
            error_html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Безопасная форма входа</title>
                <style>
                    body { font-family: Arial; margin: 40px; }
                    form { max-width: 300px; }
                    input, button { width: 100%; padding: 8px; margin: 5px 0; }
                    .error { color: red; }
                </style>
            </head>
            <body>
                <h1>Безопасная форма входа</h1>
                <p>Эта форма защищена от SQL-инъекций</p>
                
                <div class="error">Неверные учетные данные</div>
                
                <form method="POST">
                    <input type="text" name="username" placeholder="Имя пользователя" required>
                    <input type="password" name="password" placeholder="Пароль" required>
                    <button type="submit">Войти</button>
                </form>
                
                <p><strong>Попробуйте SQL-инъекцию:</strong></p>
                <p>Логин: <code>' OR '1'='1</code></p>
                <p>Пароль: <code>' OR '1'='1</code></p>
                
                <br>
                <a href="/">Назад к основной версии</a>
            </body>
            </html>
            '''
            return error_html
    
    # GET запрос - показать форму
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Безопасная форма входа</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            form { max-width: 300px; }
            input, button { width: 100%; padding: 8px; margin: 5px 0; }
            .secure { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Безопасная форма входа</h1>
        <p class="secure">Эта форма защищена от SQL-инъекций</p>
        <p>Используются параметризованные запросы SQLAlchemy</p>
        
        <form method="POST">
            <input type="text" name="username" placeholder="Имя пользователя" required>
            <input type="password" name="password" placeholder="Пароль" required>
            <button type="submit">Войти</button>
        </form>
        
        <p><strong>Попробуйте SQL-инъекцию:</strong></p>
        <p>Логин: <code>' OR '1'='1</code></p>
        <p>Пароль: <code>' OR '1'='1</code></p>
        
        <br>
        <a href="/">Назад к основной версии</a>
    </body>
    </html>
    '''

@app.route('/secure_dashboard')
def secure_dashboard():
    if 'user_id' not in session:
        return redirect('/secure_login')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Безопасная панель управления</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            .success {{ color: green; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Безопасная панель управления</h1>
        <div class="success">Успешный вход как: {session.get('username', 'Unknown')}</div>
        <p>ID пользователя: {session.get('user_id', 'Unknown')}</p>
        <p style="color: green;">Используются безопасные параметризованные запросы</p>
        <br>
        <a href="/secure_logout">Выйти</a> | 
        <a href="/">Основная версия</a>
    </body>
    </html>
    '''

@app.route('/secure_logout')
def secure_logout():
    session.clear()
    return redirect('/secure_login')

if __name__ == '__main__':
    app.run(debug=False, port=5002)