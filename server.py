import threading
import time
import socket

from flask import Flask, render_template, request, jsonify, send_from_directory

from config import TEMP_IMAGE_DIR

from app.storage import initialize_storage, add_image_from_upload
from app.metadata import load_metadata
from app.cleanup import cleanup_expired_images


app = Flask(__name__)

initialize_storage()


def run_cleanup_loop():
    """Background thread: deletes expired images every 30 seconds."""

    while True:
        try:
            cleanup_expired_images()
        except Exception as error:
            print(f"Cleanup error: {error}")

        time.sleep(30)


cleanup_thread = threading.Thread(target=run_cleanup_loop, daemon=True)
cleanup_thread.start()


def get_local_ip():
    """Finds this machine's LAN IP address (the one other devices on the
    same WiFi use to reach it) without needing any external service."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Doesn't actually send any data — just asks the OS which local
        # network interface would be used to reach an outside address.
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        sock.close()

    return ip


@app.after_request
def add_no_cache_headers(response):
    """iOS Safari aggressively caches fetch() responses and images.
    Force it to always hit the server fresh, or the iPad will keep
    showing a stale (e.g. empty) image list."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def home():
    # 127.0.0.1 / ::1 = loopback = the request originated from THIS machine (the laptop).
    # Any other remote_addr means a different device on the network (e.g. the iPad).
    if request.remote_addr in ("127.0.0.1", "::1"):
        return render_template("sender.html")

    return render_template("index.html")


@app.route("/api/lan-info")
def lan_info():
    """Tells the sender page its own LAN address, so it can render
    a QR code the iPad can scan instead of typing the IP by hand."""
    lan_ip = get_local_ip()
    return jsonify({
        "url": f"http://{lan_ip}:5000"
    })


@app.route("/api/images")
def list_images():

    try:

        metadata = load_metadata()

        image_files = []

        for file in TEMP_IMAGE_DIR.iterdir():

            if file.is_file() and file.suffix.lower() in {
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".gif"
            }:
                info = metadata.get(file.name, {})

                image_files.append({
                    "filename": file.name,
                    "added_at": info.get("added_at"),
                    "expires_at": info.get("expires_at")
                })

        # newest first
        image_files.sort(key=lambda item: item["added_at"] or "", reverse=True)

        return jsonify({
            "success": True,
            "images": image_files
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/images/<filename>")
def serve_image(filename):

    return send_from_directory(
        TEMP_IMAGE_DIR,
        filename
    )


@app.route("/api/images/<filename>", methods=["DELETE"])
def delete_image(filename):

    try:

        image_path = TEMP_IMAGE_DIR / filename

        if not image_path.exists():
            return jsonify({
                "success": False,
                "message": "Image not found."
            }), 404

        image_path.unlink()

        return jsonify({
            "success": True,
            "message": "Image deleted successfully."
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/upload", methods=["POST"])
def upload_image():

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "message": "No image received."
        }), 400


    image = request.files["image"]


    if image.filename == "":

        return jsonify({
            "success": False,
            "message": "No image selected."
        }), 400


    try:

        saved_path = add_image_from_upload(image)

        return jsonify({
            "success": True,
            "message": "Image uploaded successfully!",
            "filename": saved_path.name
        })


    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )