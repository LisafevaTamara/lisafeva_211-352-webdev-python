from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from models import *
from tools_for_cover import CoverSave, cover_delete
import bleach
import markdown
from auth import check_role

bp = Blueprint('book_tools', __name__)

BOOKS_PARAMS = ["name", "author", "short_desc", "year", "publishing_house", "count_pages"] #Изменить название переменных

def load_genre(books):
    t = 0
    for book in books:
        genres = Genres.query.join(GenresBooks).filter_by(id_book = book.id).all()
        list_genre = []
        for genre in genres:
            list_genre.append(genre.name)
        books[t].genres = list_genre
        t += 1
    return books

def get_params():
    result = {}
    error_list = {}
    input_errors = False
    for p in BOOKS_PARAMS:
        params = request.form.get(p)
        if not params:
            input_errors = True
            error_list[p] = "Ошибка ввода. Поле не может быть пустым."
            continue
        if p == "count_pages":
            if not params.isdigit():
                input_errors = True
                error_list[p] = "Ошибка ввода. Количество страниц должно быть введено числом."
        if p == "year":
            if len(params) != 4 or not params.isdigit():
                input_errors = True
                error_list[p] = "Ошибка ввода. Должен быть введен год, состоящий из четырех цифр."
        if p == "short_desc":
            params = bleach.clean(params)
        result[p] = params
    if input_errors: 
        return ("error", error_list, result)
    return result

def save_genres(id_book, new_genres_list, old_genres_list = {}):
    if old_genres_list:
        for genre in old_genres_list:
            genres_book = GenresBooks.query.filter(GenresBooks.id_book == id_book, GenresBooks.id_genre == genre).one()
            db.session.delete(genres_book)
            db.session.commit()
    for genre in new_genres_list:
        genres_book = GenresBooks(id_book = id_book, id_genre = genre)
        db.session.add(genres_book)
        db.session.commit()

def get_genres():
    genres_list = request.form.getlist('genres')
    if not genres_list:
        return ("error", {'genres' : 'Ошибка ввода. Должен быть выбран как минимум один жанр.'})
    return genres_list

def get_all_params():
    error_list = {}
    params = {}
    genres_list = []
    answer_get_params = get_params()
    answer_get_genres = get_genres()
    if "error" in answer_get_genres:
        error_list.update(answer_get_genres[1])
        
    else:
        genres_list = answer_get_genres
    if "error" in answer_get_params:
        error_list.update(answer_get_params[1])
        params.update(answer_get_params[2])
    else:
        params.update(answer_get_params)
    return (params, genres_list, error_list)
    
@bp.route('/create_book', methods=['GET', 'POST'])
@login_required
@check_role(["admin",])
def create_book():
    all_genres = Genres.query.all()
    if request.method == "POST":
        error_list = {}
        params = {}
        genres_list = []
        f = request.files.get('cover')
        if not (f and f.filename):
            error_list['cover'] = "Ошибка ввода. Поле не может быть пустым."
        
        all_params = get_all_params()
        params.update(all_params[0])
        genres_list += all_params[1]
        error_list.update(all_params[2])

        if error_list:
            flash('Ошибка ввода параметров.', 'danger')
            params['genres'] = genres_list
            return render_template('book_tools/create_book.html', genres = all_genres, errors = error_list, book = params)
        
        try:
            cover = CoverSave(f).save()
            new_book = Books(**params, cover_id = cover.id)
            db.session.add(new_book)
            db.session.commit()
            save_genres(new_book.id, genres_list)
            flash("Книга успешно добавлена.", "success")
            return redirect(url_for('index'))
        except:
            flash("При добавлении возникла ошибка.", "danger")
            db.session.rollback()
            params['genres'] = genres_list
            return render_template('book_tools/create_book.html', genres = all_genres, errors = {}, book = params)

    return render_template('book_tools/create_book.html', genres = all_genres, errors = {}, book = {})



@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@check_role(["admin","moderator"])
def edit_book(book_id):
    if not Books.query.get(book_id):
        flash('Ошибка, данной книги не существует.', 'danger')
        return redirect(url_for('index'))

    all_genres = Genres.query.all()
    book = Books.query.get(book_id)
    # Поиск жанров
    genres = Genres.query.join(GenresBooks).filter_by(id_book = book.id).all()
    genres_list = []
    for genre in genres:
        genres_list.append(genre.id)
    book.genres = genres_list
    
    if request.method == "POST":

        error_list = {}
        new_params = {}
        new_genres_list = []

        all_params = get_all_params()
        new_params.update(all_params[0])
        new_genres_list += all_params[1]
        error_list.update(all_params[2])

        if error_list:
            new_params['genres'] = new_genres_list
            flash('Ошибка ввода параметров.', 'danger')
            return render_template('book_tools/edit_book.html', genres = all_genres, errors = error_list, book = new_params)


        try:
            book.name = new_params['name']
            book.author = new_params['author']
            book.short_desc = new_params['short_desc']
            book.year = new_params['year']
            book.publishing_house = new_params['publishing_house']
            book.count_pages = new_params['count_pages']

            db.session.commit()

            save_genres(book.id, new_genres_list, genres_list)

            flash("Книга успешно изменена.", "success")
            return redirect(url_for('index'))
        except:
            flash("При изменении возникла ошибка.", "danger")
            db.session.rollback()
            new_params['genres'] = new_genres_list
            return render_template('book_tools/edit_book.html', genres = all_genres, errors = {}, book = new_params)

    return render_template('book_tools/edit_book.html', genres = all_genres, errors = {}, book = book)

@bp.route('/<int:book_id>/show')
def show_book(book_id):
    if not Books.query.get(book_id):
        flash('Ошибка, данной книги не существует.', 'danger')
        return redirect(url_for('index'))

    try:
        book = Books.query.get(book_id)
        book.short_desc = markdown.markdown(book.short_desc)
        genres = Genres.query.join(GenresBooks).filter_by(id_book = book.id).all()
        genres_list = []
        for genre in genres:
            genres_list.append(genre.name)
        str_genres = ', '.join(genres_list)
        book.genres = str_genres
        cover_storage_name = Сovers.query.get(book.cover_id).storage_filename
        cover = url_for('media', filename=cover_storage_name)
        reviews = Reviews.query.join(Users).filter(Reviews.book_id == book_id).all()
        for review in reviews:
            review.text = markdown.markdown(review.text)
        if current_user.is_authenticated:
            is_review = Reviews.query.filter(Reviews.user_id == current_user.id, Reviews.book_id == book_id).all()
        else:
            is_review = True
    except:
        flash("При загрузки страницы возникла ошибка.", "danger")

    return render_template('book_tools/show_book.html', book = book, cover = cover, reviews = reviews, is_review = is_review)

@bp.route('/<int:book_id>/delete', methods=['GET', 'POST'])
@login_required
@check_role(["admin",])
def delete_book(book_id):
    if not Books.query.get(book_id):
        flash('Ошибка, данной книги не существует.', 'danger')
        return redirect(url_for('index'))

    try:
        book = Books.query.get(book_id)

        cover_id = book.cover_id

        db.session.delete(book)
        db.session.commit()
        flash("Книга успешно удалена.", "success")

        count_book_cover = Books.query.filter(Books.cover_id == cover_id).count()
        if count_book_cover == 0:
            cover = Сovers.query.get(cover_id)
            storage_filename = cover.storage_filename
            cover_delete(storage_filename)
            db.session.delete(cover)
            db.session.commit()

    except:
        flash("При удалении возникла ошибка.", "danger")
        db.connection.rollback()
    return redirect(url_for("index"))

@bp.route('/<int:book_id>/create_review', methods=['GET', 'POST'])
@login_required
def create_review(book_id):
    if not Books.query.get(book_id):
        flash('Ошибка, данной книги не существует.', 'danger')
        return redirect(url_for('index'))

    is_review = Reviews.query.filter(Reviews.user_id == current_user.id, Reviews.book_id == book_id).all()
    if is_review:
        flash("Вы уже добавляли рецензию к этой книге.", "danger")
        return redirect(url_for('book_tools.show_book', book_id = book_id))

    book = Books.query.get(book_id)
    if request.method == "POST":
        estimation = int(request.form.get("estimation"))
        text = request.form.get("text")
        if not text:
            errors = {"text" : "Поле не может быть пустым"}
            flash("При добавлении рецензии возникла ошибка.", "danger")
            return render_template('book_tools/create_review.html', book_name = book.name, errors = errors, estimation = estimation)
        text = bleach.clean(text)

        try:
            new_review = Reviews(
                book_id = book_id, 
                user_id = current_user.id,
                estimation = estimation, 
                text = text
                )
            db.session.add(new_review)
            db.session.commit()

            flash("Рецензия успешно добавлена.", "success")
            return redirect(url_for('book_tools.show_book', book_id = book_id))
        except:
            db.connection.rollback()
            flash("При добавлении рецензии возникла ошибка.", "danger")
            return render_template('book_tools/create_review.html', book_name = book.name, errors = {}, estimation = estimation)
    return render_template('book_tools/create_review.html', book_name = book.name, errors = {})