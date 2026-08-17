from pathlib import Path
import shutil

from config import TEMP_IMAGE_DIR
from app.metadata import register_image


def initialize_storage():
    """Create the temporary image folder if it doesn't exist."""

    TEMP_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def add_image(image_path):
    """Copy an existing image into temporary storage."""

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    destination = TEMP_IMAGE_DIR / image_path.name

    shutil.copy2(
        image_path,
        destination
    )

    register_image(image_path.name)

    return destination


def add_image_from_upload(image):
    """Save an uploaded image into temporary storage."""

    filename = Path(image.filename).name

    destination = TEMP_IMAGE_DIR / filename

    image.save(destination)

    register_image(filename)

    return destination