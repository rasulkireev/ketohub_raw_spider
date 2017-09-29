import datetime
import json
import os
import urllib

from scrapy import crawler
from scrapy import spiders

from ketohub import persist
from ketohub import recipe_key


class Error(Exception):
    """Base Error class."""
    pass


class UnexpectedResponse(Error):
    """Error raised when the scraped response is in an unexpected format."""
    pass


class MissingDownloadDirectory(Error):
    """Error raised when the download directory is not defined."""
    pass


class RawContentSpider(spiders.CrawlSpider):
    """Base class to crawl keto sites and save the html and image to a local file."""
    name = 'raw_content'

    def __init__(self):
        # Directory within the download root in which to place downloaded files.
        self._download_subdir = datetime.datetime.utcnow().strftime(
            '%Y%m%d/%H%M%SZ')
        super(RawContentSpider, self).__init__()

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
        download_root = self.settings.get('DOWNLOAD_ROOT')
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
