""" Defines the spider class, RawContentSpider for the project ketohub.
"""
import os
import urllib

from datetime import datetime

from scrapy import crawler
from scrapy import spiders


class Error(Exception):
    """Base Error class."""
    pass


class UnexpectedResponse(Error):
    """Error raised when the scraped response is in an unexpected format."""
    pass


class MissingDownloadDirectory(Error):
    """Error raised when the download directory is not defined."""
    pass


def _ensure_directory_exists(directory_path):
    """Ensures the directories in directory_path exist."""
    if os.path.exists(directory_path):
        return True
    os.makedirs(directory_path)


def _write_to_file(filepath, content):
    """Writes the response content to a local file."""
    _ensure_directory_exists(os.path.dirname(filepath))
    open(os.path.join(filepath, 'indext.html'), 'w').write(content)


class RawContentSpider(spiders.CrawlSpider):
    """Base class to crawl keto sites and save  the html and image to a local file."""
    name = 'raw_content'

    def __init__(self):
        download_root = crawler.Settings().get('DOWNLOAD_ROOT')
        if not download_root:
            raise MissingDownloadDirectory(
                'Make sure you\'re providing a download directory.')
        self._filepath_prefix = os.path.join(
            download_root, datetime.utcnow().strftime('%Y%m%d/%H%M%SZ'))

        super(RawContentSpider, self).__init__()

    def _get_recipe_main_image_url(self, response):
        """Returns the URL for the recipe's primary image. Unimplemented in base class."""
        pass

    def download_recipe_contents(self, response):
        """Parses responses from the pages of individual recipes.

        Saves a recipe image as main.jpg and page html as index.html for each recipe page link
        extracted. Each recipe is saved in a location that follows this schema:

        [download_root]/YYYYMMDD/hhmmssZ/[source_domain]/[relative_url]/
         """
        # Build path for scraped files
        filepath = os.path.join(self._filepath_prefix, response.url[12:])

        # Write response body to file
        _write_to_file(filepath, response.text.encode('utf8'))

        # Find image and save it
        try:
            image_location = self._get_recipe_main_image_url(response)
        except IndexError:
            raise UnexpectedResponse('Could not extract image from page.')

        urllib.urlretrieve(image_location, os.path.join(filepath, 'main.jpg'))
