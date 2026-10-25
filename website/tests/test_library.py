"""[Lab 3] Automated tests for the library pages (Problem 2).

Like the Lab 2 tests, they replace the repository with an in-memory fake, so they run
without MySQL. The fake behaves like the real database: a book needs an existing
author (foreign key) and deleting an author deletes its books (ON DELETE CASCADE).
"""
import io
from decimal import Decimal

import pytest

from app import create_app
from app.repositories import library as library_repo


@pytest.fixture
def client(monkeypatch, tmp_path):
    authors = {}  # author_id -> row
    books = {}    # book_id -> row
    counter = {"author": 0, "book": 0}

    def list_authors():
        return [dict(a) for a in sorted(authors.values(), key=lambda a: a["author_id"])]

    def get_author(author_id):
        return dict(authors[author_id]) if author_id in authors else None

    def add_author(name, country, image=None):
        counter["author"] += 1
        authors[counter["author"]] = {"author_id": counter["author"], "name": name,
                                      "country": country, "image": image}

    def update_author(author_id, name, country, image):
        authors[author_id].update(name=name, country=country, image=image)

    def delete_author(author_id):
        authors.pop(author_id, None)
        for book_id in [b for b, row in books.items() if row["author_id"] == author_id]:
            del books[book_id]  # ON DELETE CASCADE

    def list_books():
        return [dict(b) for b in sorted(books.values(), key=lambda b: b["book_id"])]

    def list_books_of_author(author_id):
        return [dict(b) for b in books.values() if b["author_id"] == author_id]

    def get_book(book_id):
        return dict(books[book_id]) if book_id in books else None

    def add_book(title, price, author_id, image=None):
        if author_id not in authors:
            raise library_repo.UnknownAuthorError()  # foreign key fails (error 1452)
        counter["book"] += 1
        books[counter["book"]] = {"book_id": counter["book"], "title": title,
                                  "price": price, "author_id": author_id, "image": image}

    def update_book(book_id, title, price, author_id, image):
        if author_id not in authors:
            raise library_repo.UnknownAuthorError()
        books[book_id].update(title=title, price=price, author_id=author_id, image=image)

    def delete_book(book_id):
        books.pop(book_id, None)

    for name, fake in [("list_authors", list_authors), ("get_author", get_author),
                       ("add_author", add_author), ("update_author", update_author),
                       ("delete_author", delete_author), ("list_books", list_books),
                       ("list_books_of_author", list_books_of_author), ("get_book", get_book),
                       ("add_book", add_book), ("update_book", update_book),
                       ("delete_book", delete_book)]:
        monkeypatch.setattr(library_repo, name, fake)

    app = create_app()
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = str(tmp_path)  # pictures go to a temporary folder
    test_client = app.test_client()
    test_client.fake_authors = authors
    test_client.fake_books = books
    test_client.upload_folder = tmp_path
    return test_client


def make_author(client, name="Naguib Mahfouz", country="Egypt", **extra):
    return client.post("/library/authors/new", data={"name": name, "country": country, **extra},
                       content_type="multipart/form-data")


def make_book(client, title="Palace Walk", price="180.50", author_id="1", **extra):
    return client.post("/library/books/new",
                       data={"title": title, "price": price, "author_id": author_id, **extra},
                       content_type="multipart/form-data")


def picture(name="cover.png"):
    return (io.BytesIO(b"\x89PNG fake picture bytes"), name)


# ------------------------------------------------------------- F2.1 show
def test_library_page_shows_both_tables(client):
    make_author(client)
    make_book(client)
    page = client.get("/library/").get_data(as_text=True)
    assert "Palace Walk" in page and "180.50" in page
    assert "Naguib Mahfouz" in page and "Egypt" in page
    assert "author_id" in page  # the books table has the author_id column


def test_library_page_is_open_without_login(client):
    assert client.get("/library/").status_code == 200


def test_empty_library_shows_friendly_text(client):
    page = client.get("/library/").get_data(as_text=True)
    assert "No books yet" in page and "No authors yet" in page


# ------------------------------------------------------------ F2.2 add
def test_add_author(client):
    response = make_author(client)
    assert response.status_code == 302
    assert client.fake_authors[1]["name"] == "Naguib Mahfouz"


def test_add_author_validation_messages(client):
    page = make_author(client, name="  ", country="").get_data(as_text=True)
    assert "Name is required" in page and "Country is required" in page
    assert client.fake_authors == {}


def test_add_book(client):
    make_author(client)
    assert make_book(client).status_code == 302
    assert client.fake_books[1]["title"] == "Palace Walk"
    assert client.fake_books[1]["price"] == Decimal("180.50")
    assert client.fake_books[1]["author_id"] == 1


@pytest.mark.parametrize("price, message", [
    ("", "Price is required"),
    ("abc", "Price must be a number"),
    ("NaN", "Price must be a number"),
    ("-5", "Price cannot be negative"),
    ("1.999", "Price can have two decimals at most"),
    ("1000000000", "Price is too big"),
])
def test_add_book_price_rules(client, price, message):
    make_author(client)
    page = make_book(client, price=price).get_data(as_text=True)
    assert message in page
    assert client.fake_books == {}


def test_add_book_needs_title_and_author(client):
    make_author(client)
    page = make_book(client, title="", author_id="").get_data(as_text=True)
    assert "Title is required" in page and "Author is required" in page


def test_add_book_with_unknown_author_is_refused(client):
    make_author(client)
    response = make_book(client, author_id="99")  # foreign key must refuse this
    assert response.status_code == 400
    assert "That author does not exist" in response.get_data(as_text=True)
    assert client.fake_books == {}


def test_add_book_page_asks_for_an_author_first(client):
    page = client.get("/library/books/new").get_data(as_text=True)
    assert "add one first" in page


def test_sql_text_in_a_field_is_just_text(client):
    make_author(client, name="x'); DROP TABLE author;--")
    assert client.fake_authors[1]["name"] == "x'); DROP TABLE author;--"


# ----------------------------------------------------------- F2.3 edit
def test_edit_book(client):
    make_author(client)
    make_author(client, name="Agatha Christie", country="United Kingdom")
    make_book(client)
    response = client.post("/library/books/1/edit",
                           data={"title": "New title", "price": "99", "author_id": "2"},
                           content_type="multipart/form-data")
    assert response.status_code == 302
    book = client.fake_books[1]
    assert (book["title"], book["price"], book["author_id"]) == ("New title", Decimal("99.00"), 2)


def test_edit_form_is_filled_with_the_current_values(client):
    make_author(client)
    make_book(client)
    page = client.get("/library/books/1/edit").get_data(as_text=True)
    assert 'value="Palace Walk"' in page and 'value="180.50"' in page


def test_edit_author(client):
    make_author(client)
    client.post("/library/authors/1/edit", data={"name": "N. Mahfouz", "country": "Cairo"},
                content_type="multipart/form-data")
    assert client.fake_authors[1]["name"] == "N. Mahfouz"


def test_edit_missing_rows_give_404(client):
    assert client.get("/library/books/5/edit").status_code == 404
    assert client.get("/library/authors/5/edit").status_code == 404


# --------------------------------------------------- F2.4 / F2.5 remove
def test_delete_book(client):
    make_author(client)
    make_book(client)
    make_book(client, title="Other")
    assert client.post("/library/books/1/delete").status_code == 302
    assert list(client.fake_books) == [2]


def test_delete_author_deletes_their_books(client):
    make_author(client)
    make_author(client, name="Agatha Christie", country="United Kingdom")
    make_book(client, author_id="1")
    make_book(client, title="Second", author_id="1")
    make_book(client, title="Orient Express", author_id="2")
    client.post("/library/authors/1/delete")
    assert list(client.fake_authors) == [2]
    assert [b["title"] for b in client.fake_books.values()] == ["Orient Express"]


def test_delete_is_post_only(client):
    assert client.get("/library/books/1/delete").status_code == 405


# ------------------------------------------------------------ Bonus images
def test_book_cover_is_saved_and_shown(client):
    make_author(client)
    make_book(client, image=picture())
    name = client.fake_books[1]["image"]
    assert name.endswith(".png") and name != "cover.png"  # a random name is used
    assert (client.upload_folder / name).exists()
    assert name in client.get("/library/").get_data(as_text=True)


def test_wrong_picture_type_is_refused(client):
    make_author(client)
    page = make_book(client, image=(io.BytesIO(b"<?php ?>"), "evil.php")).get_data(as_text=True)
    assert "Picture must be a PNG, JPG, GIF or WEBP file" in page
    assert client.fake_books == {}
    assert list(client.upload_folder.iterdir()) == []


def test_replacing_and_removing_a_cover_deletes_the_old_file(client):
    make_author(client)
    make_book(client, image=picture())
    first = client.fake_books[1]["image"]

    client.post("/library/books/1/edit", content_type="multipart/form-data",
                data={"title": "Palace Walk", "price": "10", "author_id": "1", "image": picture("b.jpg")})
    second = client.fake_books[1]["image"]
    assert second != first and not (client.upload_folder / first).exists()

    client.post("/library/books/1/edit", content_type="multipart/form-data",
                data={"title": "Palace Walk", "price": "10", "author_id": "1", "remove_image": "1"})
    assert client.fake_books[1]["image"] is None and not (client.upload_folder / second).exists()


def test_deleting_an_author_removes_their_pictures(client):
    make_author(client, image=picture("photo.png"))
    make_book(client, image=picture())
    assert len(list(client.upload_folder.iterdir())) == 2
    client.post("/library/authors/1/delete")
    assert list(client.upload_folder.iterdir()) == []
