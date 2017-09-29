import datetime
import json
import os
import urllib

from scrapy import crawler
from scrapy import spiders

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


class ImageDownloadError(Error):
    """Failed to download the recipe main image."""
    pass

class UnexpectedImageType(Error):
    """Failed to download the recipe main image."""
    pass


def _ensure_directory_exists(directory_path):
    """Ensures the directories in directory_path exist."""
    if os.path.exists(directory_path):
        return True
    os.makedirs(directory_path)


def _write_to_file(filepath, content):
    """Writes content to a local file."""
    _ensure_directory_exists(os.path.dirname(filepath))
    open(filepath, 'wb').write(content)


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

    def download_recipe_contents(self, response):
        """Parses responses from the pages of individual recipes.

        Saves a recipe image as main.jpg and page html as index.html for each recipe page link
        extracted. Each recipe is saved in a location that follows this schema:

        [download_root]/YYYYMMDD/hhmmssZ/[source_domain]/[relative_url]/
         """
        # Build path for scraped files
        download_root = self.settings.get('DOWNLOAD_ROOT')
        if not download_root:
            raise MissingDownloadDirectory(
                'Make sure you\'re providing a download directory.')

        key = recipe_key.from_url(response.url)

        output_dir = os.path.join(download_root, self._download_subdir, key)

        # Write response body to file
        _write_to_file(
            os.path.join(output_dir, 'index.html'),
            response.text.encode('utf8'))

        # Write url to metadata file
        _write_to_file(
            os.path.join(output_dir, 'metadata.json'),
            json.dumps({
                'url': response.url
            }, indent=4, separators=(',', ':')))

        # Find image and save it
        try:
            image_url = self._get_recipe_main_image_url(response)
        except IndexError:
            raise UnexpectedResponse('Could not extract image from page.')

        image_handle = urllib.urlopen(image_url)
        if image_handle.getcode() != 200:
            raise ImageDownloadError('Failed to download image: %s, error: %d' % (image_url, image_handle.getcode()))
        if image_handle.info().type != 'image/jpeg':
            raise UnexpectedImageType('Unexpected image type: ' + image_handle.info().type)
        image_data = image_handle.read()
        _write_to_file(os.path.join(output_dir, 'main.jpg'),
                       image_data)
