import unittest

import mock

from ketohub import persist


class PersistTest(unittest.TestCase):

    def setUp(self):
        self.mock_write_to_file_fn = mock.Mock()

    def test_save_recipe_html_saves_to_correct_file(self):
        saver = persist.ContentSaver('downloads', self.mock_write_to_file_fn)
        saver.save_recipe_html('foo', '<html>Mock HTML</html>')

        self.mock_write_to_file_fn.assert_has_calls([
            mock.call('downloads/foo/index.html', '<html>Mock HTML</html>'),
        ])

    def test_save_main_image_saves_to_correct_file(self):
        saver = persist.ContentSaver('downloads', self.mock_write_to_file_fn)
        saver.save_main_image('bar', 'dummy image data')

        self.mock_write_to_file_fn.assert_has_calls([
            mock.call('downloads/bar/main.jpg', 'dummy image data'),
        ])

    def test_save_metadata_saves_to_correct_file(self):
        saver = persist.ContentSaver('downloads', self.mock_write_to_file_fn)
        saver.save_metadata('baz', {'dummy_key': 'dummy value'})

        self.mock_write_to_file_fn.assert_has_calls([
            mock.call('downloads/baz/metadata.json', """
{
    "dummy_key":"dummy value"
}""".strip()),
        ])
