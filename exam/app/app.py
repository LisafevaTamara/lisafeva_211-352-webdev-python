import math
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, request, send_from_directory
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user


app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')


# Работа с БД
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from models import *
# --------------

# Blueprint
from auth import bp as auth_bp, init_login_manager
from book_tools import bp as book_tools, load_genre
from compilations import bp as compilations
app.register_blueprint(auth_bp)
app.register_blueprint(book_tools)
app.register_blueprint(compilations)
init_login_manager(app)
# --------------

PER_PAGE = 10

@app.route('/')
def index():
    print(generate_password_hash("Qwerty123"), '')
    page = request.args.get('page', 1, type=int)
    books = Books.query.order_by(Books.year.desc()).limit(PER_PAGE).offset(PER_PAGE * (page - 1)).all()
    page_count = math.ceil(Books.query.count() / PER_PAGE)
    # Поиск жанров
    books = load_genre(books)

    # create_user()

    # Подборки
    if current_user.is_authenticated:
        compilations = Compilations.query.filter(Compilations.user_id == current_user.id).all()
    else:
        compilations = {}
        
    return render_template('index.html', books = books, page = page, page_count = page_count, compilations = compilations)


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
        )

def create_user():
    new_user = Users(
        last_name = "Фамилия",
        first_name = "Имя",
        middle_name = "Отчество",
        login = "moder",
        password_hash = generate_password_hash("Qwerty"),
        role_id = 2
    )
    db.session.add(new_user)
    db.session.commit()

    # 1. Админы:
    # Логин: fogzan Пароль: qwerty
    # Логин: psiho Пароль: Qwerty
    # 2. Модератор:
    # Логин: moder Пароль: Qwerty
    # 3. Пользователь:
    # Логин: user Пароль: Qwerty
