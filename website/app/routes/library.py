"""[Lab 3, Problem 2] Library pages: show, add, edit and remove books and authors.

F2.1 show both tables      F2.2 add a book / an author
F2.3 edit a book / an author      F2.4 remove a book      F2.5 remove an author
The library pages are open to everybody (no login), so the lab's checker can use them at once.
To make them private like the to-do list, put @login_required (from app.security) under each @bp.route.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.repositories import library as library_repo
from app.uploads import delete_image, save_image
from app.validators import validate_author, validate_book

bp = Blueprint("library", __name__, url_prefix="/library")


def back_to_library():
    return redirect(url_for("library.index"))


# ------------------------------------------------------------ [F2.1] show
@bp.get("/")
def index():
    authors = library_repo.list_authors()
    books = library_repo.list_books()
    author_names = {a["author_id"]: a["name"] for a in authors}  # name of each author_id (no JOIN)
    book_counts = {}
    for book in books:
        book_counts[book["author_id"]] = book_counts.get(book["author_id"], 0) + 1
    return render_template(
        "library.html",
        books=books,
        authors=authors,
        author_names=author_names,
        book_counts=book_counts,
    )


# ------------------------------------------------------- books: add / edit
def render_book_form(book=None, form=None, errors=None, status=200):
    authors = library_repo.list_authors()  # fills the "Author" drop-down
    return render_template(
        "book_form.html",
        book=book,
        form=form or {},
        errors=errors or {},
        authors=authors,
    ), status


@bp.route("/books/new", methods=["GET", "POST"])
def add_book():
    if request.method == "GET":
        return render_book_form()

    form = {
        "title": request.form.get("title", "").strip(),
        "price": request.form.get("price", ""),
        "author_id": request.form.get("author_id", ""),
    }
    errors, price, author_id = validate_book(form["title"], form["price"], form["author_id"])  # [R8]
    image_name = None
    if not errors:
        image_name, image_error = save_image(request.files.get("image"))
        if image_error:
            errors["image"] = image_error
    if errors:
        return render_book_form(form=form, errors=errors, status=400)

    try:
        library_repo.add_book(form["title"], price, author_id, image_name)  # [F2.2]
    except library_repo.UnknownAuthorError:  # foreign key: that author does not exist
        delete_image(image_name)
        return render_book_form(form=form, errors={"author_id": "That author does not exist"}, status=400)
    flash("Book added")
    return back_to_library()


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = library_repo.get_book(book_id)
    if book is None:
        abort(404)
    if request.method == "GET":
        form = {"title": book["title"], "price": str(book["price"]), "author_id": str(book["author_id"])}
        return render_book_form(book=book, form=form)

    form = {
        "title": request.form.get("title", "").strip(),
        "price": request.form.get("price", ""),
        "author_id": request.form.get("author_id", ""),
    }
    errors, price, author_id = validate_book(form["title"], form["price"], form["author_id"])  # [R8]
    new_image = None
    if not errors:
        new_image, image_error = save_image(request.files.get("image"))
        if image_error:
            errors["image"] = image_error
    if errors:
        return render_book_form(book=book, form=form, errors=errors, status=400)

    remove_old = request.form.get("remove_image") == "1"
    image = new_image or (None if remove_old else book["image"])  # the file name that stays in the database
    try:
        library_repo.update_book(book_id, form["title"], price, author_id, image)  # [F2.3]
    except library_repo.UnknownAuthorError:
        delete_image(new_image)
        return render_book_form(book=book, form=form, errors={"author_id": "That author does not exist"}, status=400)
    if image != book["image"]:
        delete_image(book["image"])  # the old cover is not used any more
    flash("Book saved")
    return back_to_library()


@bp.post("/books/<int:book_id>/delete")
def delete_book(book_id):
    book = library_repo.get_book(book_id)
    if book is None:
        abort(404)
    library_repo.delete_book(book_id)  # [F2.4]
    delete_image(book["image"])
    flash("Book removed")
    return back_to_library()


# ----------------------------------------------------- authors: add / edit
def render_author_form(author=None, form=None, errors=None, status=200):
    return render_template(
        "author_form.html", author=author, form=form or {}, errors=errors or {}
    ), status


@bp.route("/authors/new", methods=["GET", "POST"])
def add_author():
    if request.method == "GET":
        return render_author_form()

    form = {"name": request.form.get("name", "").strip(), "country": request.form.get("country", "").strip()}
    errors = validate_author(form["name"], form["country"])  # [R8]
    image_name = None
    if not errors:
        image_name, image_error = save_image(request.files.get("image"))
        if image_error:
            errors["image"] = image_error
    if errors:
        return render_author_form(form=form, errors=errors, status=400)

    library_repo.add_author(form["name"], form["country"], image_name)  # [F2.2]
    flash("Author added")
    return back_to_library()


@bp.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    author = library_repo.get_author(author_id)
    if author is None:
        abort(404)
    if request.method == "GET":
        return render_author_form(author=author, form={"name": author["name"], "country": author["country"]})

    form = {"name": request.form.get("name", "").strip(), "country": request.form.get("country", "").strip()}
    errors = validate_author(form["name"], form["country"])  # [R8]
    new_image = None
    if not errors:
        new_image, image_error = save_image(request.files.get("image"))
        if image_error:
            errors["image"] = image_error
    if errors:
        return render_author_form(author=author, form=form, errors=errors, status=400)

    remove_old = request.form.get("remove_image") == "1"
    image = new_image or (None if remove_old else author["image"])
    library_repo.update_author(author_id, form["name"], form["country"], image)  # [F2.3]
    if image != author["image"]:
        delete_image(author["image"])
    flash("Author saved")
    return back_to_library()


@bp.post("/authors/<int:author_id>/delete")
def delete_author(author_id):
    author = library_repo.get_author(author_id)
    if author is None:
        abort(404)
    books = library_repo.list_books_of_author(author_id)  # their covers must be removed too
    library_repo.delete_author(author_id)  # [F2.5] ON DELETE CASCADE removes the books in MySQL
    delete_image(author["image"])
    for book in books:
        delete_image(book["image"])
    flash("Author removed" + (f" together with {len(books)} book(s)" if books else ""))
    return back_to_library()
