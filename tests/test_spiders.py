import unittest

from scrapy import http

from ketohub import spiders


class FindKetoConnectImageUrlTest(unittest.TestCase):

    def test_finds_correct_image_on_simple_page(self):
        self.assertEqual(
            spiders.find_ketoconnect_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body="""
                    <html>
                      <img src="images/foo.jpg" />
                      <img src="images/correct_image.jpg" />
                    </html>""")), 'images/correct_image.jpg')


class FindRuledMeImageUrlTest(unittest.TestCase):

    def test_finds_correct_image_on_simple_page(self):
        self.assertEqual(
            spiders.find_ruled_me_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body="""
                    <html>
                      <img src="images/correct_image.jpg" />
                      <img src="images/foo.jpg" />
                    </html>""")), 'images/correct_image.jpg')
