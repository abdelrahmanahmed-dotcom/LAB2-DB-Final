"""[Lab 3, Bonus] Book covers and author photos.

A picture is saved in app/static/uploads/ under a random name (the name the user
chose is never used, so nobody can overwrite another file). The database keeps
only that file name.
"""
import os
import uuid

from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_IMAGE_BYTES = 2 * 1024 * 1024  # 2 MB


def save_image(file_storage):
    """Save an uploaded picture. Returns (file name or None, error message or None).

    No file chosen is not an error: it returns (None, None).
    """
    if file_storage is None or not file_storage.filename:
        return None, None
    extension = file_storage.filename.rsplit(".", 1)[-1].lower() if "." in file_storage.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        return None, "Picture must be a PNG, JPG, GIF or WEBP file"

    data = file_storage.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        return None, "The picture is too big (2 MB at most)"
    if not data:
        return None, "The picture file is empty"

    name = f"{uuid.uuid4().hex}.{extension}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "wb") as out:
        out.write(data)
    return name, None


def delete_image(file_name):
    """Remove a picture file (does nothing when there is none)."""
    if not file_name:
        return
    # only a plain file name is ever stored, but never trust it to build a path
    safe_name = os.path.basename(file_name)
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
    try:
        os.remove(path)
    except OSError:
        pass
