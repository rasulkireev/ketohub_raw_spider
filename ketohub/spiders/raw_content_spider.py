""" Defines the spider class, RawContentSpider for the project ketohub.
"""
import errno
import os
import urllib

from datetime import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


def get_image_location(response):
    """ Locates the image element and src. """
    if 'ketoconnect' in response.url:
        return response.css('img')[1].xpath('@src').extract_first()

    if 'ruled.me' in response.url:
        return response.css('img').xpath('@src').extract_first()


def write_to_file(filepath, filename, content):
    """ Writes the response content to a local file. """
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

    with open(filepath + filename, 'w+') as open_file:
        open_file.write(content)


class RawContentSpider(CrawlSpider):
    """ Spider to crawl keto sites and save the html and image to a local file for each recipe. """
    name = 'raw_content'
    allowed_domains = ['ruled.me', 'ketoconnect.net']
    start_urls = [
        'https://www.ruled.me/keto-recipes/',
        'https://www.ketoconnect.net/recipes/'
    ]

    rules = [
        # Extract links for food category pages ex: https://ketoconnect.net/recipes/desserts/
        Rule(
            LinkExtractor(allow=[
                r'https://ketonnect.com/\w+(-\w+)+/',
                r'https://www.ruled.me/keto-recipes/\w+/'
            ])),

        # Extract links for finding additional pages within food category pages
        # ex: https://www.ruled.me/keto-recipes/dinner/page/2/
        Rule(
            LinkExtractor(
                allow=r'https://www.ruled.me/keto-recipes/\w+/page/\d+/')),

        # Extract links for the actual recipes
        # ex: https://www.ketoconnect.net/recipe/spicy-cilantro-dressing/
        # ex: https://www.ruled.me/easy-keto-cordon-bleu/
        Rule(
            LinkExtractor(allow=[
                r'https://www.ruled.me/(\w+-)+\w+/',
                r'https://www.ketoconnect.net/recipe/(\w+-)+\w+/'
            ]),
            callback='parse_recipe',
            follow=False)
    ]

    def __init__(self):
        self.scrape_start_time = datetime.utcnow()
        super(RawContentSpider, self).__init__()

    def parse_recipe(self, response):
        """ Parses responses from the pages of individual recipes.

        Saves a recipe image as main.jpg and page html as index.html for each recipe page link
        extracted. Each recipe is saved in a location that follows this schema:

        [download_root]/YYYYMMDD/hhmmssZ/[source_domain]/[relative_url]/
         """
        # Build path for scraped files
        filepath = '{download_root}/{scrape_start_time}/{source_url}'.format(
            download_root=self.settings.get('DOWNLOAD_ROOT'),
            scrape_start_time=self.scrape_start_time.strftime('%Y%m%d/%H%M%SZ'),
            source_url=response.url[12:])

        # Write response body to file
        write_to_file(filepath, 'index.html', response.text.encode('utf8'))

        # Find image and save it
        image_location = get_image_location(response)
        urllib.urlretrieve(image_location, '%smain.jpg' % filepath)
