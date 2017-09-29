import unittest

import mock

from ketohub import persist


class PersistTest(unittest.TestCase):

    def setUp(self):
        self.mock_write_to_file_fn = mock.Mock()

    def test_save_recipe_html_saves_to_correct_file(self):
        saver = persist.ContentSaver('downloads/foo',
                                     self.mock_write_to_file_fn)
        saver.save_recipe_html('<html>Mock HTML</html>')

        self.mock_write_to_file_fn.assert_has_calls([
            mock.call('downloads/foo/index.html', '<html>Mock HTML</html>'),
        ])

    def test_save_main_image_saves_to_correct_file(self):
        saver = persist.ContentSaver('downloads/foo',
                                     self.mock_write_to_file_fn)
        saver.save_main_image('dummy image data')

        self.mock_write_to_file_fn.assert_has_calls([
            mock.call('downloads/foo/main.jpg', 'dummy image data'),
        ])

    def test_save_metadata_saves_to_correct_file(self):
        saver = persist.ContentSaver('downloads/foo',
                                     self.mock_write_to_file_fn)
        saver.save_metadata({'dummy_key': 'dummy value'})

        self.mock_write_to_file_fn.assert_has_calls([
            mock.call('downloads/foo/metadata.json', """
{
    "dummy_key":"dummy value"
}""".strip()),
        ])
