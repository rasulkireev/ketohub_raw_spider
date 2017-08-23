""" Defines the spider class, RawContentSpider for the project ketohub.
"""
import scrapy


class RawContentSpider(scrapy.Spider):
    """ Dummy spider class. """
    name = "raw_content"
    allowed_domains = []

    def parse(self, response):
        return
