from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import LoginManager,UserMixin, login_user, logout_user, current_user
from app import db
from models import Users
from functools import wraps
from sqlalchemy import text

bp = Blueprint('auth', __name__)

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)

class User(UserMixin):
    def __init__(self, user_id, user_login, role_id):
        self.id = user_id
        self.login = user_login
        self.role_id = role_id

def load_user(user_id):
    user = db.session.execute(db.select(Users).filter_by(id=user_id)).scalar()
    return user

def check_role(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            roles_id = []
            if "admin" in roles:
                roles_id.append(current_app.config["ADMIN_ROLE_ID"])
            if "moderator" in roles:
                roles_id.append(current_app.config["MODERATOR_ROLE_ID"])
            if "user" in roles:
                roles_id.append(current_app.config["USER_ROLE_ID"])

            if not (current_user.role_id in roles_id):
                flash("Недостаточно прав для доступа к странице", "warning")
                return redirect(url_for("index"))
            return func(*args, **kwargs)
        return wrapper
    return decorator

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['loginInput']
        password = request.form['passwordInput']
        remember_me = request.form.get('remember_me') == 'on'
        if login and password:
            # user = db.session.execute(db.select(Users).filter_by(login=login)).scalar()
            query = text('''
            SELECT * FROM users WHERE login = :login and password_hash = SHA2(:password, 256);
            ''')
        
            user = db.session.execute(query, {"login": login, "password": password}).fetchone()

            if user:
                login_user(User(user.id, user.login, user.role_id), remember=remember_me)
                flash('Вы успешно аутентифицированы.', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('index'))
        flash('Введены неверные логин и/или пароль.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))