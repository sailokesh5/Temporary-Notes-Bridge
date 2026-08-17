import json
from datetime import datetime, timedelta

from config import TEMP_IMAGE_DIR, EXPIRATION_HOURS


METADATA_FILE = TEMP_IMAGE_DIR / "metadata.json"


def load_metadata():
    """Load image metadata from the metadata file."""

    if not METADATA_FILE.exists():
        return {}

    with open(METADATA_FILE, "r") as file:
        return json.load(file)


def save_metadata(metadata):
    """Save image metadata."""

    with open(METADATA_FILE, "w") as file:
        json.dump(metadata, file, indent=4)


def register_image(image_name):
    """Register an image and calculate its expiration time."""

    metadata = load_metadata()

    added_at = datetime.now()
    expires_at = added_at + timedelta(hours=EXPIRATION_HOURS)

    metadata[image_name] = {
        "added_at": added_at.isoformat(),
        "expires_at": expires_at.isoformat()
    }

    save_metadata(metadata)