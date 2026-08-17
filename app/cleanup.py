from pathlib import Path
from datetime import datetime

from app.metadata import load_metadata, save_metadata
from config import TEMP_IMAGE_DIR


def cleanup_expired_images():
    """Delete images whose expiration time has passed."""

    metadata = load_metadata()

    current_time = datetime.now()

    remaining_metadata = {}

    for image_name, image_info in metadata.items():

        expires_at = datetime.fromisoformat(image_info["expires_at"])

        image_path = TEMP_IMAGE_DIR / image_name

        if current_time >= expires_at:

            if image_path.exists():
                image_path.unlink()

            print(f"Deleted expired image: {image_name}")

        else:
            remaining_metadata[image_name] = image_info

    save_metadata(remaining_metadata)