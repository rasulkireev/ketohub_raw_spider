from scrapy import http

from ketohub.spiders import ruled_me_crawl_spider
import tests.test_raw_content_spider


class RuledMeCrawlSpiderTest(
        tests.test_raw_content_spider.RawContentSpiderTest):
    """Test case for the ruled_me_raw_content spider."""

    def test_get_recipe_main_image_url_returns_first_image(self):
        """Tests that the first image location is extracted."""
        file_content = (
            "<html><img src='images/right_image.jpg'><img src='images/wrong_image.jpg'></html>"
        )

        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body=file_content)

        spider = ruled_me_crawl_spider.RuledMeCrawlSpider()
        spider.settings = self.mock_settings
        spider.download_recipe_contents(response)

        self.urlopen_patch.assert_called_once_with('images/right_image.jpg')
