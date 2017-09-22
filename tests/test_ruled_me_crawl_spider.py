""" Unit tests for the class RuledMeCrawlSpider.
"""
from scrapy import http

from ketohub.spiders import ruled_me_crawl_spider
import tests.test_raw_content_spider


class RuledMeCrawlSpiderTest(
        tests.test_raw_content_spider.RawContentSpiderTest):
    """Test case for the ruled_me_raw_content spider."""

    def test_get_recipe_main_image_url_returns_first_image(self):  #pylint: disable=invalid-name
        """Tests that the first image location is extracted."""
        file_content = (
            "<html><img src='images/right_image.jpg'><img src='images/wrong_image.jpg'></html>"
        )

        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body=file_content)

        self.mock_settings.get.return_value = '/foo/download/root'
        spider = ruled_me_crawl_spider.RuledMeCrawlSpider()
        spider.download_recipe_contents(response)

        # Make sure _write_to_file is called with correct arguments from get_recipe_main_image
        self.urllib_patch.assert_called_with(
            'images/right_image.jpg',
            '/foo/download/root/20170102/030405Z/foo.com/main.jpg')
