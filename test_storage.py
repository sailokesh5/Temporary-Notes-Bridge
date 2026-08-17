from tkinter import Tk, filedialog

from app.storage import initialize_storage, add_image


# Initialize temporary storage
initialize_storage()


# Open file picker
root = Tk()
root.withdraw()

image_path = filedialog.askopenfilename(
    title="Select an image",
    filetypes=[
        ("Image files", "*.png *.jpg *.jpeg *.gif *.webp"),
        ("All files", "*.*")
    ]
)

root.destroy()


# Check whether an image was selected
if not image_path:
    print("No image selected.")
else:
    copied_image = add_image(image_path)

    print("Image copied successfully!")
    print(f"Temporary location: {copied_image}")