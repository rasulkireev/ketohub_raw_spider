import datetime
import io
import unittest

import mock
from scrapy import http

from ketohub.spiders import raw_content_spider


class RawContentSpiderTest(unittest.TestCase):
    """Test case for the raw_content spider."""

    def setUp(self):
        mock_urlopen = mock.patch(
            'ketohub.spiders.raw_content_spider.urllib.urlopen', autospec=True)
        self.addCleanup(mock_urlopen.stop)
        self.urlopen_patch = mock_urlopen.start()

        self.mock_start_scrape_time = datetime.datetime(
            year=2017, month=1, day=2, hour=3, minute=4, second=5)
        mock_datetime = mock.patch(
            'ketohub.spiders.raw_content_spider.datetime.datetime')
        self.addCleanup(mock_datetime.stop)
        datetime_patch = mock_datetime.start()
        datetime_patch.utcnow.return_value = self.mock_start_scrape_time

        mock_content_saver = mock.patch(
            'ketohub.spiders.raw_content_spider.persist.ContentSaver')
        self.addCleanup(mock_content_saver.stop)
        self.content_saver_patch = mock_content_saver.start()
        self.mock_saver = mock.Mock()
        self.content_saver_patch.return_value = self.mock_saver

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

        self.get_image_patch.return_value = 'https://mock.com/test_image.jpg'
        self.urlopen_patch.return_value = io.BytesIO('dummy image data')
        spider = raw_content_spider.RawContentSpider()
        spider.download_recipe_contents(response)

        self.content_saver_patch.assert_called_once_with(
            'download_output/20170102/030405Z/foo-com')
        self.mock_saver.save_recipe_html.assert_called_once_with(
            '<html></html>')
        self.mock_saver.save_metadata.assert_called_once_with({
            'url':
            'https://www.foo.com',
        })
        self.mock_saver.save_main_image.assert_called_once_with(
            'dummy image data')

        self.urlopen_patch.assert_called_with('https://mock.com/test_image.jpg')

    def test_download_recipe_contents_with_an_empty_response(self):
        """Tests that download recipe contents raises an error on an empty response."""
        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body='')

        self.get_image_patch.side_effect = IndexError
        spider = raw_content_spider.RawContentSpider()

        with self.assertRaises(raw_content_spider.UnexpectedResponse):
            spider.download_recipe_contents(response)
