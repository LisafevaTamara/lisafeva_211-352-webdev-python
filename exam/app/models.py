import os
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import current_app
from app import db

class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Roles %r>' % self.name



class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def __repr__(self):
        return '<Users %r>' % self.login
    
    @property
    def is_admin(self):
        return self.role_id == current_app.config["ADMIN_ROLE_ID"]
    
    @property
    def is_moderator(self):
        return self.role_id == current_app.config["MODERATOR_ROLE_ID"]
    
    @property
    def is_user(self):
        return self.role_id == current_app.config["USER_ROLE_ID"]


  
class Books(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    # как обозначить только год я не нашел, поэтому сделаю через int
    year = db.Column(db.Integer, nullable=False)
    publishing_house = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    count_pages = db.Column(db.Integer, nullable=False)
    # Так как у нескольких книг может быть одна и та же обложка, то длгичнее вписывать id обложки в книгу, а не наоборот
    cover_id = db.Column(db.String(100), db.ForeignKey('covers.id'), nullable=False)

    def __repr__(self):
        return '<Books %r>' % self.name
    
    @property
    def count_reviews(self):
        count = Reviews.query.filter(Reviews.book_id == self.id).count()
        return count
    
    @property
    def estimation(self):
        count = Reviews.query.filter(Reviews.book_id == self.id).count()
        if count == 0:
            return 0
        reviews = Reviews.query.filter(Reviews.book_id == self.id).all()
        summ = 0
        for review in reviews:
            summ += review.estimation
        result = summ / count
        return round(result,2)


class Genres(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return '<Genres %r>' % self.name



class GenresBooks(db.Model):
    __tablename__ = 'genres_books'

    id = db.Column(db.Integer, primary_key=True)
    id_book = db.Column(db.Integer, db.ForeignKey('books.id'))
    id_genre = db.Column(db.Integer, db.ForeignKey('genres.id'))



class Сovers(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.String(100), primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return '<Сovers %r>' % self.file_name
    
    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext


class Reviews(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    estimation = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    def __repr__(self):
        return '<Reviews %r>' % self.text
    
    @property
    def get_name_user(self):
        user = Users.query.get(self.user_id)
        return user.full_name
    

class Compilations(db.Model):
    __tablename__ = 'compilations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Reviews %r>' % self.text
    
    @property
    def count_book(self):
        count = CompilationsBooks.query.filter_by(id_compilation = self.id).count()
        return count
    

class CompilationsBooks(db.Model):
    __tablename__ = 'compilations_books'

    id = db.Column(db.Integer, primary_key=True)
    id_compilation = db.Column(db.Integer, db.ForeignKey('compilations.id'), nullable=False)
    id_book = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)