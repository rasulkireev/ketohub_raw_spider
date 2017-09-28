import unittest

import mock
from scrapy import http

from ketohub.spiders import raw_content_spider


class RawContentSpiderTest(unittest.TestCase):
    """Test case for the raw_content spider."""

    def setUp(self):
        mock_urllib = mock.patch(
            'ketohub.spiders.raw_content_spider.urllib.urlretrieve',
            autospec=True)
        self.addCleanup(mock_urllib.stop)
        self.urllib_patch = mock_urllib.start()

        mock_write_to_file = mock.patch(
            'ketohub.spiders.raw_content_spider._write_to_file')
        self.addCleanup(mock_write_to_file.stop)
        self.write_to_file_patch = mock_write_to_file.start()

        mock_get_recipe_main_image = mock.patch(
            'ketohub.spiders.raw_content_spider.RawContentSpider._get_recipe_main_image_url'
        )
        self.addCleanup(mock_get_recipe_main_image.stop)
        self.get_image_patch = mock_get_recipe_main_image.start()

    def test_download_recipe_contents_with_a_simple_response(self):
        """Tests that download_recipe_contents works as expected for a simple response."""
        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body='<html></html>')

        self.get_image_patch.return_value = 'test_image.jpg'
        spider = raw_content_spider.RawContentSpider()
        spider._filepath_prefix = '/foo/download/root/20170102/030405Z'
        spider.download_recipe_contents(response)

        self.write_to_file_patch.assert_has_calls([
            mock.call('/foo/download/root/20170102/030405Z/foo-com',
                      'index.html', '<html></html>'),
            mock.call('/foo/download/root/20170102/030405Z/foo-com',
                      'metadata.json', '{\n    "url":"https://www.foo.com"\n}')
        ])

        self.urllib_patch.assert_called_with(
            'test_image.jpg',
            '/foo/download/root/20170102/030405Z/foo-com/main.jpg')

    def test_download_recipe_contents_with_an_empty_response(self):
        """Tests that download recipe contents raises an error on an empty response."""
        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body='')

        self.get_image_patch.side_effect = IndexError
        spider = raw_content_spider.RawContentSpider()
        spider._filepath_prefix = '/mock/download/root//20170102/030405Z'

        with self.assertRaises(raw_content_spider.UnexpectedResponse):
            spider.download_recipe_contents(response)

    def test_that_undefined_download_folder_location_raises_error(self):
        """Tests that download_recipe_contents raises an error with an undefined download folder."""
        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body='')

        mock_settings = mock.Mock()
        mock_settings.get.return_value = None
        spider = raw_content_spider.RawContentSpider()
        spider.settings = mock_settings

        with self.assertRaises(raw_content_spider.MissingDownloadDirectory):
            spider.download_recipe_contents(response)

    def test_format_recipe_key_with_simple_url(self):
        """Tests that _format_recipe_key returns an the recipe key as expected."""
        spider = raw_content_spider.RawContentSpider()
        actual_key = spider._format_recipe_key(
            'https://www.mock.com/Mikes_Chicken_Kiev/')

        self.assertEqual(actual_key, 'mock-com_mikes-chicken-kiev')
