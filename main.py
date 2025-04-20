import json
import os
import tkinter as tk
from PIL import Image, ImageTk
from dotenv import dotenv_values
from enum import Enum

class VISITED(Enum):
    NOT_VISITED = 1
    VISITED = 2
    MARKED = 3

config = dotenv_values(".env")
SOURCE_FOLDER = config['SOURCE_FOLDER']

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
        if os.path.exists(VISITED_JSON):
            print('here')
            with open(VISITED_JSON, 'r') as fd:
                self.filter = json.load(fd)
            self.filter = {k: v for k, v in self.filter.items() if "\\.thumbnails\\" not in k}
            self.image_paths = list(self.filter.keys())
            self.idx = 0
            while self.filter[self.image_paths[self.idx]] != VISITED.NOT_VISITED.value:
                self.idx += 1
        else:
            print("first time running, creating empty filter")
            self.image_paths = image_paths
            self.filter = {path: VISITED.NOT_VISITED.value for path in image_paths}
            self.idx = 0
        self.marked = 0
        for k,v in self.filter.items():
            if v == VISITED.MARKED.value:
                self.marked += 1
        self.state("zoomed")
        self.bind("<Escape>", self.escape_pressed)

        self.update_idletasks()
        self.screen_width = int(self.winfo_screenwidth() * 0.8)
        self.screen_height = int(self.winfo_screenheight() * 0.8)
        self.target_size = (self.screen_width, self.screen_height)

        self.label = tk.Label(self, bg="black", width=self.screen_width, height=self.screen_height)
        self.label.pack(fill=tk.BOTH, expand=True)

        self.status = tk.Label(self, text="", font=("Arial", 16), bg="black", fg="white")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.visit()
        self.show_image()

        self.bind("<Left>", self.prev_image)
        self.bind("<Right>", self.next_image)
        self.bind("<space>", self.toggle_mark)
        self.focus_set()

    def dispaly_status(self):
        path = self.image_paths[self.idx]
        marked = self.filter[path] == VISITED.MARKED.value
        marked_txt = "[MARKED]\t" if marked else ""
        rel_path = os.path.relpath(path, SOURCE_FOLDER)
        self.status.config(
            text=f"{marked_txt}\t{self.idx + 1}/{len(self.image_paths)}\t{rel_path} ({self.marked} or {int(self.marked/self.idx*100)}% marked)",
            fg="lightgreen" if marked else "white"
        )


    def show_image(self):
        path = self.image_paths[self.idx]
        image = Image.open(path)

        background = Image.new("RGB", self.target_size, (0, 0, 0))
        image.thumbnail(self.target_size, Image.Resampling.LANCZOS)
        x = (self.target_size[0] - image.width) // 2
        y = (self.target_size[1] - image.height) // 2
        background.paste(image, (x, y))
        self.photo = ImageTk.PhotoImage(background)
        self.label.config(image=self.photo)
        self.label.image = self.photo
        self.dispaly_status()

    def visit(self):
        if self.filter[self.image_paths[self.idx]] == VISITED.NOT_VISITED.value:
            self.filter[self.image_paths[self.idx]] = VISITED.VISITED.value
    
    def mark(self):
        self.filter[self.image_paths[self.idx]] = VISITED.MARKED.value
        self.next_image(event=None)

    def unmark(self):
        self.filter[self.image_paths[self.idx]] = VISITED.VISITED.value
        self.dispaly_status()

    def toggle_mark(self, event):
        if self.filter[self.image_paths[self.idx]] == VISITED.MARKED.value:
            self.unmark()
            self.marked -= 1
        else:
            self.mark()
            self.marked += 1

    def save_filter(self):
        with open(VISITED_JSON, 'w') as fd:
            json.dump(self.filter, fd, indent=2)
            print('saved')

    def prev_image(self, event):
        if self.idx > 0:
            self.idx -= 1
            self.show_image()

    def next_image(self, event):
        if self.idx < len(self.image_paths) - 1:
            self.idx += 1
            self.visit()
            self.show_image()
            if (self.idx + 1) % 100 == 0:
                self.save_filter()


    def escape_pressed(self, event):
        self.save_filter()
        self.destroy()

def main():
    all_images = get_all_images(SOURCE_FOLDER)
    app = ImageViewer(all_images)
    app.mainloop()

if __name__ == "__main__":
    main()
