import io
import unittest
import urllib2

import mock

from ketohub import images


class ImagesTest(unittest.TestCase):

    def setUp(self):
        mock_urlopen = mock.patch(
            'ketohub.images.urllib2.urlopen', autospec=True)
        self.addCleanup(mock_urlopen.stop)
        self.urlopen_patch = mock_urlopen.start()

    def test_download_succeeds_when_server_is_ok(self):
        self.urlopen_patch.return_value = io.BytesIO('dummy image data')
        self.assertEqual(
            images.download_data('http://mock.com/image.jpg'),
            'dummy image data')
        self.urlopen_patch.assert_called_once_with('http://mock.com/image.jpg')

    def test_download_succeeds_when_server_returns_403(self):
        self.urlopen_patch.side_effect = urllib2.HTTPError(
            url='', code=404, msg='', hdrs=None, fp=None)
        with self.assertRaises(urllib2.HTTPError):
            images.download_data('http://mock.com/image.jpg')
        self.urlopen_patch.assert_called_once_with('http://mock.com/image.jpg')
