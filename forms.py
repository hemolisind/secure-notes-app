from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import html
import re

def validate_username_safe(form, field):
    """Валидатор для проверки безопасных символов в имени пользователя"""
    if field.data:
        # Запрещаем HTML-теги и специальные символы
        if re.search(r'[<>"\']', field.data):
            raise ValidationError('Имя пользователя содержит запрещенные символы')

class SafeStringField(StringField):
    """Поле строки с автоматическим экранированием HTML"""
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = html.escape(valuelist[0].strip())

class SafeTextAreaField(TextAreaField):
    """Поле текста с автоматическим экранированием HTML"""
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = html.escape(valuelist[0].strip())

class NoteForm(FlaskForm):
    title = SafeStringField('Заголовок', validators=[
        DataRequired(message='Заголовок обязателен'), 
        Length(max=100, message='Заголовок не более 100 символов')
    ])
    content = SafeTextAreaField('Содержание', validators=[
        DataRequired(message='Содержание обязательно')
    ])
    submit = SubmitField('Сохранить')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'), 
        Length(min=4, max=20, message='Имя пользователя должно быть от 4 до 20 символов'),
        validate_username_safe  
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'), 
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтверждение пароля обязательно'), 
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен')
    ])
    submit = SubmitField('Войти')