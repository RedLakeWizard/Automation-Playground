import os
import uuid

from PIL import Image
from flask import current_app
from werkzeug.datastructures import FileStorage


def save_product_image(image: FileStorage) -> str:
    """
    Save and resize an uploaded image to static/images and return its URL path.
    """
    if not image or image.filename == "":
        return ""

    filename = f"{uuid.uuid4().hex}.jpg"
    images_path = os.path.join(current_app.root_path, "static", "images")
    os.makedirs(images_path, exist_ok=True)

    filepath = os.path.join(images_path, filename)
    img = Image.open(image.stream).convert("RGB")
    img.thumbnail((1200, 1200))
    img.save(filepath, format="JPEG", quality=85)

    return f"/static/images/{filename}"
