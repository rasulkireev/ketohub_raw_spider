from scrapy import linkextractors
from scrapy import spiders

import ketohub.spiders.raw_content_spider


class KetoconnectCrawlSpider(
        ketohub.spiders.raw_content_spider.RawContentSpider):
    """Spider to crawl ketoconnect.com. Inherits from RawContentSpider class."""
    name = 'ketoconnect_raw_content'
    allowed_domains = ['ketoconnect.net']
    start_urls = ['https://www.ketoconnect.net/recipes/']

    rules = [
        # Extract links for food category pages ex: https://ketoconnect.net/recipes/desserts/
        spiders.Rule(
            linkextractors.LinkExtractor(allow=[
                r'https://ketonnect.com/\w+(-\w+)+/',
            ])),

        # Extract links for the actual recipes
        # ex: https://www.ketoconnect.net/recipe/spicy-cilantro-dressing/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=[r'https://www.ketoconnect.net/recipe/\w+(-\w+)+/']),
            callback='_download_recipe_contents',
            follow=False)
    ]

    def _get_recipe_main_image_url(self, response):
        """Returns the URL for the recipe's primary image."""
        return str(response.css('img')[1].xpath('@src').extract_first())
