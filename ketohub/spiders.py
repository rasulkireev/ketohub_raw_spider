import datetime
import os
import urllib

from scrapy import conf
from scrapy import linkextractors
from scrapy import spiders

import persist
import recipe_key


class Error(Exception):
    """Base Error class."""
    pass


class UnexpectedResponse(Error):
    """Error raised when the scraped response is in an unexpected format."""
    pass


class MissingDownloadDirectory(Error):
    """Error raised when the download directory is not defined."""
    pass


class SpiderBase(spiders.CrawlSpider):
    """Crawl sites and save the HTML and image to a local file."""
    name = 'raw_content'

    def __init__(self):
        # Directory within the download root in which to place downloaded files.
        self._download_subdir = datetime.datetime.utcnow().strftime(
            '%Y%m%d/%H%M%SZ')
        super(SpiderBase, self).__init__()

    def _get_recipe_main_image_url(self, response):
        """Returns the URL for the recipe's primary image.

        Child classes must override this method.

        Args:
            response: Page response object.

        Returns:
            The URL for the main recipe image.
        """
        pass

    def _make_content_saver(self, url):
        download_root = conf.settings.get('DOWNLOAD_ROOT')
        if not download_root:
            raise MissingDownloadDirectory(
                'Make sure you\'re providing a download directory.')

        key = recipe_key.from_url(url)

        output_dir = os.path.join(download_root, self._download_subdir, key)
        return persist.ContentSaver(output_dir)

    def download_recipe_contents(self, response):
        """Parses responses from the pages of individual recipes.

        Saves a recipe image as main.jpg and page html as index.html for each recipe page link
        extracted. Each recipe is saved in a location that follows this schema:

        [download_root]/YYYYMMDD/hhmmssZ/[source_domain]/[relative_url]/
         """
        content_saver = self._make_content_saver(response.url)
        content_saver.save_recipe_html(response.text.encode('utf8'))
        content_saver.save_metadata({'url': response.url})

        # Find image and save it
        try:
            image_url = self._get_recipe_main_image_url(response)

        except IndexError:
            raise UnexpectedResponse('Could not extract image from page.')

        image_handle = urllib.urlopen(image_url)
        content_saver.save_main_image(image_handle.read())


class KetoConnectSpider(SpiderBase):
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
            callback='download_recipe_contents',
            follow=False)
    ]

    def _get_recipe_main_image_url(self, response):
        """Returns the URL for the recipe's primary image."""
        return str(response.css('img')[1].xpath('@src').extract_first())


class RuledMeSpider(SpiderBase):
    name = 'ruled_me_raw_content'
    allowed_domains = ['ruled.me']
    start_urls = ['https://www.ruled.me/keto-recipes/']

    rules = [
        # Extract links for food category pages ex: https://www.ruled.me/keto-recipes/breakfast/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=[r'https://www.ruled.me/keto-recipes/\w+/'])),

        # Extract links for finding additional pages within food category pages
        # ex: https://www.ruled.me/keto-recipes/dinner/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ruled.me/keto-recipes/\w+/page/\d+/')),

        # Extract links for the actual recipes
        # ex: https://www.ruled.me/easy-keto-cordon-bleu/
        spiders.Rule(
            linkextractors.LinkExtractor(allow=[
                r'https://www.ruled.me/(\w+-)+\w+/',
            ]),
            callback='download_recipe_contents',
            follow=False)
    ]

    def _get_recipe_main_image_url(self, response):
        """Returns the URL for the recipe's primary image."""
        return str(response.css('img').xpath('@src').extract_first())
