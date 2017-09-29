from scrapy import http

from ketohub.spiders import ketoconnect_crawl_spider
import tests.test_raw_content_spider


class KetoconnectCrawlSpiderTest(
        tests.test_raw_content_spider.RawContentSpiderTest):
    """Test case for the ketoconnect_raw_content spider."""

    def test_get_recipe_main_image_url_returns_second_image(self):
        """Tests that the correct second image is extracted."""
        file_content = (
            "<html><img src='images/wrong_image.jpg'><img src='images/right_image.jpg'></html>"
        )

        response = http.TextResponse(
            url='https://www.foo.com',
            request=http.Request('https://www.foo.com'),
            body=file_content)

        spider = ketoconnect_crawl_spider.KetoconnectCrawlSpider()
        spider.settings = self.mock_settings
        spider.download_recipe_contents(response)

        self.urlopen_patch.assert_called_with('images/right_image.jpg')
