""" Unit tests for the class RawContentSpider.
"""
from __future__ import absolute_import

import datetime
import unittest

import mock

from ketohub.spiders import raw_content_spider
from scrapy.http import TextResponse, Request


class TestSpider(raw_content_spider.RawContentSpider):
    """ Test class for mocking the RawContentSpider. """

    def __init__(self):
        self.settings = mock.Mock()
        self.settings.get.return_value = '/path/to/foo'
        super(TestSpider, self).__init__()


class RawContentSpiderTest(unittest.TestCase):
    """ Test case for the raw_content spider. """

    def setUp(self):
        mock_urllib = mock.patch(
            'ketohub.spiders.raw_content_spider.urllib.urlretrieve',
            autospec=True)
        self.addCleanup(mock_urllib.stop)
        self.urllib_patch = mock_urllib.start()

        self.mock_start_scrape_time = datetime.datetime(
            year=2017, day=1, month=1)
        mock_datetime = mock.patch(
            'ketohub.spiders.raw_content_spider.datetime')
        self.addCleanup(mock_datetime.stop)
        datetime_patch = mock_datetime.start()
        datetime_patch.utcnow.return_value = self.mock_start_scrape_time

        mock_write_to_file = mock.patch(
            'ketohub.spiders.raw_content_spider.write_to_file')
        self.addCleanup(mock_write_to_file.stop)
        self.write_to_file_patch = mock_write_to_file.start()

        self.spider = TestSpider()

    def build_expected_filepath(self, url):
        """ Returns the expected filepath for a specific url. """
        return '{download_root}/{scrape_start_time}/{source_url}'.format(
            download_root='/path/to/foo',
            scrape_start_time=self.mock_start_scrape_time.strftime(
                '%Y%m%d/%H%M%SZ'),
            source_url=url[12:])

    def test_offline_for_get_image_location_response_from_ketoconnect(self):  #pylint: disable=invalid-name
        """Tests that parse_recipe wextracts the correct img src for a ketoconnect response."""
        mock_url = 'https://www.ketoconnect.com/test/'
        request = Request(mock_url)
        file_content = "<html><img src='first_image.jpg'><img src='second_image.jpg'></html>"
        response = TextResponse(
            url=mock_url, request=request, body=file_content)

        self.spider.parse_recipe(response)

        # Make sure write_to_file is called with correct arguments
        self.urllib_patch.assert_called_with(
            'second_image.jpg',
            '%smain.jpg' % self.build_expected_filepath(mock_url))

    def test_offline_for_get_image_location_response_from_ruled(self):  #pylint: disable=invalid-name
        """Tests that parse_recipe works extracts the correct img src for a ruled.me response."""
        mock_url = 'https://www.ruled.me/keto-recipes/test/'
        request = Request(mock_url)
        file_content = "<html><img src='first_image.jpg'><img src='second_image.jpg'></html>"
        response = TextResponse(
            url=mock_url, request=request, body=file_content)

        self.spider.parse_recipe(response)
        self.urllib_patch.assert_called_with(
            'first_image.jpg',
            '%smain.jpg' % self.build_expected_filepath(mock_url))

    def test_offline_parse_recipe_with_a_simple_response(self):  #pylint: disable=invalid-name
        """ Tests that the callback parse_recipe works as expected on a simple, offline response."""
        mock_url = 'https://www.foo.com'
        request = Request(mock_url)
        file_content = "<html><body></body></html>"
        response = TextResponse(
            url=mock_url, request=request, body=file_content)

        self.spider.parse_recipe(response)
        self.write_to_file_patch.assert_called_with(
            self.build_expected_filepath(mock_url), 'index.html', file_content)

    def test_offline_parse_recipe_with_an_empty_response(self):  #pylint: disable=invalid-name
        """ Tests that the callback parse_recipe works as expected on an empty response."""
        mock_url = 'https://www.foo.com'
        request = Request(mock_url)
        file_content = ''
        response = TextResponse(
            url=mock_url, request=request, body=file_content)

        self.spider.parse_recipe(response)
        self.write_to_file_patch.assert_called_with(
            self.build_expected_filepath(mock_url), 'index.html', file_content)
