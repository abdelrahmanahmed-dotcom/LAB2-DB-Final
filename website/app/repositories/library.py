"""[Lab 3] All SQL about the library database (tables author and book).

Only simple SELECT, INSERT, UPDATE and DELETE (no JOIN). Every statement uses %s
placeholders, so values are never glued into the SQL.
The foreign key book.author_id -> author.author_id has ON DELETE CASCADE, so
deleting an author makes MySQL delete that author's books too.
"""
import pymysql

from app.db import get_library_db

MYSQL_FK_FAILS = 1452  # "a foreign key constraint fails" (book.author_id does not exist)


class UnknownAuthorError(Exception):
    """Raised when a book points at an author_id that is not in the author table."""


# ---------------------------------------------------------------- authors
def list_authors():
    """[F2.1] All authors."""
    with get_library_db().cursor() as cur:
        cur.execute("SELECT author_id, name, country, image FROM author ORDER BY author_id")
        return cur.fetchall()


def get_author(author_id):
    with get_library_db().cursor() as cur:
        cur.execute(
            "SELECT author_id, name, country, image FROM author WHERE author_id = %s",
            (author_id,),
        )
        return cur.fetchone()  # a dict, or None


def add_author(name, country, image=None):
    """[F2.2] Add an author."""
    with get_library_db().cursor() as cur:
        cur.execute(
            "INSERT INTO author (name, country, image) VALUES (%s, %s, %s)",
            (name, country, image),
        )


def update_author(author_id, name, country, image):
    """[F2.3] Edit an author (image is the file name to keep, or None for no photo)."""
    with get_library_db().cursor() as cur:
        cur.execute(
            "UPDATE author SET name = %s, country = %s, image = %s WHERE author_id = %s",
            (name, country, image, author_id),
        )


def delete_author(author_id):
    """[F2.5] Delete an author. ON DELETE CASCADE deletes all of the author's books too."""
    with get_library_db().cursor() as cur:
        cur.execute("DELETE FROM author WHERE author_id = %s", (author_id,))


# ------------------------------------------------------------------ books
def list_books():
    """[F2.1] All books, with the author_id of each one."""
    with get_library_db().cursor() as cur:
        cur.execute("SELECT book_id, title, price, author_id, image FROM book ORDER BY book_id")
        return cur.fetchall()


def list_books_of_author(author_id):
    """Used before deleting an author, to also remove the cover files of the cascaded books."""
    with get_library_db().cursor() as cur:
        cur.execute("SELECT book_id, image FROM book WHERE author_id = %s", (author_id,))
        return cur.fetchall()


def get_book(book_id):
    with get_library_db().cursor() as cur:
        cur.execute(
            "SELECT book_id, title, price, author_id, image FROM book WHERE book_id = %s",
            (book_id,),
        )
        return cur.fetchone()


def add_book(title, price, author_id, image=None):
    """[F2.2] Add a book. MySQL refuses an author_id that does not exist (error 1452)."""
    try:
        with get_library_db().cursor() as cur:
            cur.execute(
                "INSERT INTO book (title, price, author_id, image) VALUES (%s, %s, %s, %s)",
                (title, price, author_id, image),
            )
    except pymysql.err.IntegrityError as error:
        if error.args[0] == MYSQL_FK_FAILS:
            raise UnknownAuthorError() from error
        raise


def update_book(book_id, title, price, author_id, image):
    """[F2.3] Edit a book."""
    try:
        with get_library_db().cursor() as cur:
            cur.execute(
                "UPDATE book SET title = %s, price = %s, author_id = %s, image = %s "
                "WHERE book_id = %s",
                (title, price, author_id, image, book_id),
            )
    except pymysql.err.IntegrityError as error:
        if error.args[0] == MYSQL_FK_FAILS:
            raise UnknownAuthorError() from error
        raise


def delete_book(book_id):
    """[F2.4] Delete a book."""
    with get_library_db().cursor() as cur:
        cur.execute("DELETE FROM book WHERE book_id = %s", (book_id,))
