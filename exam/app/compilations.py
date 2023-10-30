from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from book_tools import load_genre
from models import *
from auth import check_role


bp = Blueprint('compilations', __name__)

@bp.route('/list_compilation')
@login_required
@check_role(["user",])
def list_compilation():
    сompilations = Compilations.query.filter_by(user_id = current_user.id).all()
    return render_template('compilations/list_compilation.html', compilations = сompilations)


@bp.route('/create_compilation', methods = ['POST'])
@login_required
@check_role(["user",])
def create_compilation():
    name = request.form.get('name')
    try:
        new_compilation = Compilations(
            user_id = current_user.id,
            name = name
        )
        db.session.add(new_compilation)
        db.session.commit()
        flash("Книга успешно добавлена.", "success")
    except:
        flash("При добавлении возникла ошибка.", "danger")
        db.session.rollback()
    return redirect(url_for("compilations.list_compilation"))


@bp.route('/<int:compilation_id>/delete_compilation', methods = ['POST', 'GET'])
@login_required
@check_role(["user",])
def delete_compilation(compilation_id):
    if not Compilations.query.get(compilation_id):
        flash('Ошибка, данной подборки не существует.', 'danger')
        return redirect(url_for('index'))

    try:
        compilation = Compilations.query.get(compilation_id)
        db.session.delete(compilation)
        db.session.commit()
        flash("Подборка книг успешно добавлена.", "success")
    except:
        flash("При добавлении подборки книг возникла ошибка.", "danger")
        db.session.rollback()
    return redirect(url_for("compilations.list_compilation"))


@bp.route('/<int:compilation_id>/show_compilation')
@login_required
@check_role(["user",])
def show_compilation(compilation_id):
    if not Compilations.query.get(compilation_id):
        flash('Ошибка, данной подборки не существует.', 'danger')
        return redirect(url_for('index'))

    try:
        compilation = Compilations.query.get(compilation_id)
        books = Books.query.join(CompilationsBooks).filter_by(id_compilation = compilation_id).all() 
        books = load_genre(books)
    except:
        flash("При загрузки подборки книг возникла ошибка.", "danger")

    return render_template('compilations/show_compilation.html', books = books, compilation = compilation)

@bp.route('/<int:book_id>/add_book_in_compilation', methods=["POST", "GET"])
@login_required
@check_role(["user",])
def add_book_in_compilation(book_id):
    if not Books.query.get(book_id):
        flash('Ошибка, данной книги не существует.', 'danger')
        return redirect(url_for('index'))

    try:
        compilation_id = request.form.get('compilations')
        
        test_compilation_books = CompilationsBooks.query.filter_by(id_compilation = compilation_id, id_book = book_id).count()
        if test_compilation_books != 0:
            flash("Такая книга уже есть в этой подборке.", "warning")
            return redirect(url_for("index"))

        compilations_books = CompilationsBooks(
            id_compilation = compilation_id,
            id_book = book_id
        )
        db.session.add(compilations_books)
        db.session.commit()

        flash("Книга в подборку успешно добавлена.", "success")
    except:
        flash("При добавлении книги в подборку возникла ошибка.", "danger")

    return redirect(url_for("index"))