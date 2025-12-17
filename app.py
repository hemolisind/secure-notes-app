import os
import html
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Note, User
from forms import NoteForm, RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key-only')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

db.init_app(app)

def escape_html_content(text):
    if text is None:
        return ""
    return html.escape(str(text))

@app.template_filter('escape_html')
def escape_html_filter(text):
    return escape_html_content(text)

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
        "base-uri 'self';"
        "form-action 'self';"
        "object-src 'none';"
    )
    
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Server'] = 'Unknown'
    
    if 'user_id' in session:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

def create_test_user():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='test').first():
            test_user = User(
                username='test',
                password=generate_password_hash('test123')
            )
            db.session.add(test_user)
            db.session.commit()

create_test_user()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_note_ownership(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != session['user_id']:
        flash('У вас нет прав для редактирования этой заметки', 'danger')
        return False
    return note

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    notes = Note.query.filter_by(user_id=user.id).all()
    form = NoteForm()
    
    safe_username = escape_html_content(user.username)
    
    return render_template('index.html', notes=notes, form=form, username=safe_username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return render_template('register.html', form=form)
            
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь войдите в систему.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session.permanent = True
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login'))

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    form = NoteForm()
    
    if form.validate_on_submit():
        safe_title = escape_html_content(form.title.data.strip())
        safe_content = escape_html_content(form.content.data.strip())
        
        new_note = Note(
            title=safe_title,
            content=safe_content,
            user_id=session['user_id']
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Заметка успешно добавлена!', 'success')
        return redirect(url_for('index'))
    else:
        if form.title.errors:
            for error in form.title.errors:
                flash(f'Ошибка в заголовке: {error}', 'danger')
        if form.content.errors:
            for error in form.content.errors:
                flash(f'Ошибка в содержании: {error}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = check_note_ownership(note_id)
    if not note:
        return redirect(url_for('index'))
    
    form = NoteForm(obj=note)
    if form.validate_on_submit():
        note.title = escape_html_content(form.title.data.strip())
        note.content = escape_html_content(form.content.data.strip())
        db.session.commit()
        flash('Заметка успешно обновлена!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', form=form, note=note)

@app.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = check_note_ownership(note_id)
    if not note:
        return redirect(url_for('index'))
    
    db.session.delete(note)
    db.session.commit()
    flash('Заметка успешно удалена!', 'success')
    return redirect(url_for('index'))

@app.route('/test_sql_injection')
def test_sql_injection():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Тестирование SQL-инъекций</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .danger { color: red; font-weight: bold; }
            .warning { color: orange; }
        </style>
    </head>
    <body>
        <h1>Тестирование SQL-инъекций</h1>
        
        <div class="warning">
            <h2>Уязвимая версия</h2>
            <p>Эта версия использует конкатенацию строк и уязвима к SQL-инъекциям</p>
            <a href="http://localhost:5001/vulnerable_login" style="color: red; font-weight: bold;">
                Перейти к уязвимой форме входа
            </a>
        </div>
        
        <br>
        
        <div style="color: green;">
            <h2>Безопасная версия</h2>
            <p>Эта версия использует параметризованные запросы SQLAlchemy</p>
            <a href="/login">Перейти к безопасной форме входа</a>
        </div>
        []
        <br>
        <hr>
        
        <h3>Примеры SQL-инъекций для тестирования:</h3>
        <ul>
            <li><code>' OR '1'='1</code> - базовый обход аутентификации</li>
            <li><code>' OR 1=1--</code> - комментарий в SQL</li>
            <li><code>admin' --</code> - вход как admin без пароля</li>
            <li><code>' UNION SELECT 1,2,3--</code> - UNION атака</li>
        </ul>
    </body>
    </html>
    '''

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='localhost', port=5000)
    #  Уязвимый код для тестирования
DEBUG = True  # Критическая уязвимость
SECRET_KEY = 'weak-password-123'  # Критическая уязвимость

def unsafe_query(user_input):
    # SQL-инъекция через f-строку
    return f"SELECT * FROM users WHERE name = '{user_input}'"