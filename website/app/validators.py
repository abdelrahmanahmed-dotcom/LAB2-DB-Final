"""[R8] Validation rules with the exact messages from the lab.

The server runs these again even though JavaScript already checked in the browser,
because anybody can send a request without using our page.
Each function returns a dict {field_name: message}; an empty dict means "all good".
"""
from datetime import date
from decimal import Decimal, InvalidOperation

MAX_NAME = 100        # users.name is VARCHAR(100)
MAX_EMAIL = 255       # users.email is VARCHAR(255)
MAX_TITLE = 200       # todos.title is VARCHAR(200)
MAX_PASSWORD_BYTES = 72  # bcrypt only reads the first 72 bytes


def validate_register(name, email, password, confirm_password):
    errors = {}
    if not name.strip():
        errors["name"] = "Name is required"
    elif len(name) > MAX_NAME:
        errors["name"] = f"Name is too long ({MAX_NAME} characters at most)"

    if not email.strip():
        errors["email"] = "Email is required"
    elif "@" not in email:
        errors["email"] = "Email must contain @"
    elif len(email) > MAX_EMAIL:
        errors["email"] = f"Email is too long ({MAX_EMAIL} characters at most)"

    if not password:
        errors["password"] = "Password is required"
    elif len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        errors["password"] = f"Password is too long ({MAX_PASSWORD_BYTES} characters at most)"

    if not confirm_password:
        errors["confirm_password"] = "Confirm password is required"
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"
    return errors


def validate_login(email, password):
    errors = {}
    if not email.strip():
        errors["email"] = "Email is required"
    elif "@" not in email:
        errors["email"] = "Email must contain @"
    if not password:
        errors["password"] = "Password is required"
    return errors


def validate_title(title):
    """Used for both adding and editing a to-do. Returns a message or None."""
    if not title.strip():  # empty or only spaces
        return "Title is required"
    if len(title.strip()) > MAX_TITLE:
        return f"Title is too long ({MAX_TITLE} characters at most)"
    return None


def parse_due_date(text):
    """[Bonus: due dates] Returns (date or None, error message or None). An empty field is allowed."""
    text = text.strip()
    if not text:
        return None, None
    try:
        return date.fromisoformat(text), None  # the browser sends YYYY-MM-DD
    except ValueError:
        return None, "Due date is not a valid date"


# ---------------------------------------------------------------- [Lab 3] library
MAX_AUTHOR_NAME = 100   # author.name is VARCHAR(100)
MAX_COUNTRY = 50        # author.country is VARCHAR(50)
MAX_BOOK_TITLE = 200    # book.title is VARCHAR(200)
MAX_PRICE = Decimal("99999999.99")  # book.price is DECIMAL(10,2)


def validate_author(name, country):
    """[F2.2][F2.3] Returns {field: message}; empty means all good."""
    errors = {}
    if not name.strip():
        errors["name"] = "Name is required"
    elif len(name.strip()) > MAX_AUTHOR_NAME:
        errors["name"] = f"Name is too long ({MAX_AUTHOR_NAME} characters at most)"
    if not country.strip():
        errors["country"] = "Country is required"
    elif len(country.strip()) > MAX_COUNTRY:
        errors["country"] = f"Country is too long ({MAX_COUNTRY} characters at most)"
    return errors


def parse_price(text):
    """Returns (Decimal or None, error message or None). Two decimals at most, like DECIMAL(10,2)."""
    text = text.strip()
    if not text:
        return None, "Price is required"
    try:
        price = Decimal(text)
    except InvalidOperation:
        return None, "Price must be a number"
    if not price.is_finite():  # 'NaN' and 'Infinity' are accepted by Decimal
        return None, "Price must be a number"
    if price < 0:
        return None, "Price cannot be negative"
    if price != price.quantize(Decimal("0.01")):
        return None, "Price can have two decimals at most"
    if price > MAX_PRICE:
        return None, "Price is too big"
    return price.quantize(Decimal("0.01")), None


def validate_book(title, price_text, author_id_text):
    """[F2.2][F2.3] Returns (errors, price, author_id)."""
    errors = {}
    if not title.strip():
        errors["title"] = "Title is required"
    elif len(title.strip()) > MAX_BOOK_TITLE:
        errors["title"] = f"Title is too long ({MAX_BOOK_TITLE} characters at most)"

    price, price_error = parse_price(price_text)
    if price_error:
        errors["price"] = price_error

    author_id = None
    author_id_text = author_id_text.strip()
    if not author_id_text:
        errors["author_id"] = "Author is required"
    elif not author_id_text.isdigit() or int(author_id_text) > 2147483647:  # INT range
        errors["author_id"] = "Author is not valid"
    else:
        author_id = int(author_id_text)
    return errors, price, author_id
