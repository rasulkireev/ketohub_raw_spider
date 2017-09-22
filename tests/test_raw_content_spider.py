import datetime
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

        self.mock_start_scrape_time = datetime.datetime(
            year=2017, month=1, day=2, hour=3, minute=4, second=5)
        mock_datetime = mock.patch(
            'ketohub.spiders.raw_content_spider.datetime')
        self.addCleanup(mock_datetime.stop)
        datetime_patch = mock_datetime.start()
        datetime_patch.utcnow.return_value = self.mock_start_scrape_time

        mock_write_to_file = mock.patch(
            'ketohub.spiders.raw_content_spider._write_to_file')
        self.addCleanup(mock_write_to_file.stop)
        self.write_to_file_patch = mock_write_to_file.start()

        self.mock_settings = mock.Mock()
        mock_settings = mock.patch(
            'ketohub.spiders.raw_content_spider.crawler.Settings',
            return_value=self.mock_settings)
        self.addCleanup(mock_settings.stop)
        mock_settings.start()

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

        self.mock_settings.get.return_value = '/foo/download/root'
        self.get_image_patch.return_value = 'test_image.jpg'
        spider = raw_content_spider.RawContentSpider()
        spider.download_recipe_contents(response)

        self.write_to_file_patch.assert_called_with(
            '/foo/download/root/20170102/030405Z/foo.com', '<html></html>')

        # Make sure _write_to_file is called with correct arguments.
        self.urllib_patch.assert_called_with(
            'test_image.jpg',
            '/foo/download/root/20170102/030405Z/foo.com/main.jpg')

    def test_download_recipe_contents_with_an_empty_response(self):
        """Tests that download recipe contents raises an error on an empty response."""
        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body='')

        self.mock_settings.get.return_value = '/mock/download/root'
        self.get_image_patch.side_effect = IndexError
        spider = raw_content_spider.RawContentSpider()

        with self.assertRaises(raw_content_spider.UnexpectedResponse):
            spider.download_recipe_contents(response)

    def test_that_undefined_download_folder_location_raises_error(self):
        """Tests that download_recipe_contents raises an error with an undefined download folder."""
        self.mock_settings.get.return_value = None

        with self.assertRaises(raw_content_spider.MissingDownloadDirectory):
            raw_content_spider.RawContentSpider()
