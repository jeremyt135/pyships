from PIL import Image, ImageTk

class ImageLoader:
    def __init__(self):
        self._cache = dict()

    def load(self, file_path: str) -> Image:
        if file_path not in self._cache:
            self._cache[file_path] = Image.open(file_path)

        return self._cache[file_path]

instance = ImageLoader()
      