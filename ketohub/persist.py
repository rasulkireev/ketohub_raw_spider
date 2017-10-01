import json
import os


def _ensure_directory_exists(directory_path):
    """Ensures the directories in directory_path exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def _write_to_file(filepath, content):
    """writes content to a local file."""
    _ensure_directory_exists(os.path.dirname(filepath))
    open(filepath, 'wb').write(content)


class ContentSaver(object):
    """Saves recipe content to disk."""

    def __init__(self, root, write_file_fn=_write_to_file):
        self._root = root
        self._write_file_fn = write_file_fn

    def save_metadata(self, key, metadata):
        self._write_file_fn(
            self._output_path(key, 'metadata.json'),
            json.dumps(metadata, indent=4, separators=(',', ':')))

    def save_recipe_html(self, key, recipe_html):
        self._write_file_fn(self._output_path(key, 'index.html'), recipe_html)

    def save_main_image(self, key, main_image_data):
        self._write_file_fn(self._output_path(key, 'main.jpg'), main_image_data)

    def _output_path(self, key, filename):
        return os.path.join(self._root, key, filename)
