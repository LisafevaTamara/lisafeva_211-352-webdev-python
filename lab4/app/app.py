from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from mysql_db import MySQL
import mysql.connector

PERMITED_PARAMS = ['login', 'password', 'last_name', 'first_name', 'middle_name', 'role_id']
EDIT_PARAMS = ['last_name', 'first_name', 'middle_name', 'role_id']

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице нужно пройти процедуру аутентификации'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login

@login_manager.user_loader
def load_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
    if user:
        return User(user.id, user.login)
    return None

def load_roles():
    query = 'SELECT * FROM roles;'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        roles = cursor.fetchall()
    return roles

def extract_params(params_list):
    params_dict = {param: request.form.get(param) or None for param in params_list}
    return params_dict

def none_error(params):
    none_error_list = [key for key, value in params.items() if value is None]
    return none_error_list

def login_error(login):
    login_text_error = ''
    allowed_symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    if any(char not in allowed_symbols for char in login):
        login_text_error = 'Логин может состоять только из латинских букв'
    if len(login) < 5:
        if login_text_error == '':
            login_text_error = 'Логин должен быть >= 5 символов'
        else:
            login_text_error += '. Логин должен быть >= 5 символов'
    return login_text_error

def password_error(password):
    password_text_error = ''
    allowed_symbols = '~!?@#$%^&*_-+()[]{}></\|"\'.,:;'
    count_b = any(char.isupper() for char in password)
    count_s = any(char.islower() for char in password)
    count_nums = any(char.isdigit() for char in password)

    if len(password) < 8 or len(password) > 128:
        password_text_error = 'Пароль должен быть 8 < пароль < 128 символов.'
    elif not all(char.isalnum() or char in allowed_symbols for char in password):
        password_text_error = 'Пароль может состоять только из латинских или кириллических букв и символов {}.'.format(allowed_symbols)
    elif not count_b or not count_s:
        password_text_error = 'Пароль должен иметь, как минимум, одну заглавную и одну строчную букву.'
    elif not count_nums:
        password_text_error = 'Пароль должен иметь, как минимум, одну цифру и может включать в себя только арабские цифры.'
    
    return password_text_error

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        remember = request.form.get('remember_me') == 'on'

        query = 'SELECT * FROM users WHERE login = %s and password_hash = SHA2(%s, 256);'
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (login, password))
            print(cursor.statement)
            user = cursor.fetchone()

        if user:
            login_user(User(user.id, user.login), remember = remember)
            flash('Вы успешно прошли аутентификацию!', 'success')
            param_url = request.args.get('next')
            return redirect(param_url or url_for('index'))
        flash('Введён неправильный логин или пароль.', 'danger')
    return render_template('login.html')

@app.route('/users')
def users():
    query = 'SELECT users.*, roles.name AS role_name FROM users LEFT JOIN roles ON roles.id = users.role_id'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        users_list = cursor.fetchall()
    
    return render_template('users.html', users_list=users_list)

@app.route('/users/new')
@login_required
def users_new():
    roles_list = load_roles()
    return render_template('users_new.html', roles_list=roles_list, user={})

@app.route('/users/create', methods=['POST'])
@login_required
def create_user():
    params = extract_params(PERMITED_PARAMS)
    none_error_list = none_error(params)
    if params['login']:
        login_text_error = login_error(params['login'])
    else:
        login_text_error = ''
    if params['password']:
        password_text_error = password_error(params['password'])
    else:
        password_text_error = ''
    if not none_error_list or login_text_error != '' or password_text_error != '':
        return render_template('users_new.html', user = params, roles_list = load_roles(), none_error_list = none_error_list, login_text_error = login_text_error, password_text_error = password_text_error)
    query = 'INSERT INTO users(login, password_hash, last_name, first_name, middle_name, role_id) VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);'
    try:
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            db.connection().commit()
            flash('Успешно!', 'success')
    except mysql.connector.errors.DatabaseError:    
        db.connection().rollback()
        flash('При сохранении данных возникла ошибка.', 'danger')
        return render_template('users_new.html', user = params, roles_list = load_roles(), none_error_list = none_error_list, login_text_error = login_text_error, password_text_error = password_text_error)
    
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user(user_id):
    params = extract_params(EDIT_PARAMS)
    params['id'] = user_id
    none_error_list = none_error(params)
    query = ('UPDATE users SET last_name=%(last_name)s, first_name=%(first_name)s, '
             'middle_name=%(middle_name)s, role_id=%(role_id)s WHERE id=%(id)s;')
    try:
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            db.connection().commit()
            flash('Успешно!', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash('При сохранении данных возникла ошибка.', 'danger')
        return render_template('users_edit.html', user = params, roles_list = load_roles(), none_error_list = none_error_list)

    return redirect(url_for('users'))

@app.route('/<int:user_id>/change_password', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    none_error_list = []
    password_text_error = ''
    error_passwords = []
    if request.method == 'POST':
        params = extract_params(['old_password', 'new_password', 'repeat_new_password'])
        none_error_list = none_error(params)
        if none_error_list:
            return render_template('change_password.html', none_error_list = none_error_list)
        if params['new_password']:
            password_text_error = password_error(params['new_password'])
            if params['new_password'] != params['repeat_new_password']:
                error_passwords.append('repeat_new_password')
        
        query_select = ('SELECT * FROM users WHERE id=%s and password_hash = SHA2(%s, 256);')
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query_select, (user_id, params['old_password']))
            print(cursor.statement)
            user = cursor.fetchone()
        if user and not error_passwords and password_text_error == '':
            query_update = ('UPDATE users SET password_hash = SHA2(%s, 256) WHERE id=%s;')
            try:
                with db.connection().cursor(named_tuple=True) as cursor:
                    cursor.execute(query_update, (params['old_password'], user_id))
                    db.connection().commit()
                    flash('Пароль Изменён', 'success')
                    return redirect(url_for('index'))
            except mysql.connector.errors.DatabaseError:
                db.connection().rollback()
                flash('При сохранении данных возникла ошибка.', 'danger')
        elif not user:
            error_passwords.append('old_password')
    return render_template('change_password.html', none_error_list = none_error_list, password_text_error = password_text_error, error_passwords = error_passwords)

@app.route('/users/<int:user_id>/edit')
@login_required
def edit_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('users_edit.html', user=user, roles_list = load_roles())


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    query = 'DELETE FROM users WHERE users.id=%s;'
    try:
        cursor = db.connection().cursor(named_tuple=True)
        cursor.execute(query, (user_id,))
        db.connection().commit()
        cursor.close()
        flash('Пользователь успешно удален', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash('При удалении пользователя возникла ошибка.', 'danger')
    return redirect(url_for('users'))

@app.route('/user/<int:user_id>')
def show_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('users_show.html', user=user)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))