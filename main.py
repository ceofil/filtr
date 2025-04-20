import json
import os
import tkinter as tk
from PIL import Image, ImageTk
from dotenv import dotenv_values

config = dotenv_values(".env")
SOURCE_FOLDER = config['SOURCE_FOLDER']
TARGET_FOLDER = config['TARGET_FOLDER']

VISITED_JSON = 'visited.json'

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')

def get_all_images(folder):
    image_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_files.append(os.path.join(root, file))
    return sorted(image_files)



class ImageViewer(tk.Tk):
    def __init__(self, image_paths):
        super().__init__()
        self.title("Image Viewer")
        self.image_paths = image_paths
        self.idx = 0

        self.state("zoomed")
        self.bind("<Escape>", lambda e: self.destroy())  # Press Esc to exit

        self.update_idletasks()
        self.screen_width = int(self.winfo_screenwidth() * 0.8)
        self.screen_height = int(self.winfo_screenheight() * 0.8)
        self.target_size = (self.screen_width, self.screen_height)

        self.label = tk.Label(self, bg="black", width=self.screen_width, height=self.screen_height)
        self.label.pack(fill=tk.BOTH, expand=True)

        self.status = tk.Label(self, text="", font=("Arial", 16), bg="black", fg="white")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.configure(bg='lightblue')
        self.show_image()

        self.bind("<Left>", self.prev_image)
        self.bind("<Right>", self.next_image)
        self.focus_set()

    def show_image(self):
        image = Image.open(self.image_paths[self.idx])

        background = Image.new("RGB", self.target_size, (0, 0, 0))
        image.thumbnail(self.target_size, Image.Resampling.LANCZOS)
        x = (self.target_size[0] - image.width) // 2
        y = (self.target_size[1] - image.height) // 2
        background.paste(image, (x, y))
        self.photo = ImageTk.PhotoImage(background)
        self.label.config(image=self.photo)
        self.label.image = self.photo
        self.status.config(
            text=f"{self.idx + 1}/{len(self.image_paths)}\t{self.image_paths[self.idx]}"
        )

    def prev_image(self, event):
        if self.idx > 0:
            self.idx -= 1
            self.show_image()

    def next_image(self, event):
        if self.idx < len(self.image_paths) - 1:
            self.idx += 1
            self.show_image()

def main():
    all_images = get_all_images(SOURCE_FOLDER)
    app = ImageViewer(all_images)
    app.mainloop()

if __name__ == "__main__":
    main()
