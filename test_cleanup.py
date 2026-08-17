from datetime import datetime, timedelta

from app.metadata import load_metadata, save_metadata
from app.cleanup import cleanup_expired_images


metadata = load_metadata()

if not metadata:
    print("No images found in metadata.")
else:

    # Make every image appear expired
    expired_time = datetime.now() - timedelta(minutes=1)

    for image_name in metadata:
        metadata[image_name]["expires_at"] = expired_time.isoformat()

    save_metadata(metadata)

    print("Images have been marked as expired.")

    # Run cleanup
    cleanup_expired_images()