import unittest

from scrapy import http

from ketohub import spiders


class FindKetoConnectImageUrlTest(unittest.TestCase):

    def test_finds_image_from_opengraph(self):
        self.assertEqual(
            spiders.find_ketoconnect_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body="""
<html>
  <meta property="og:image" content="https://mock.com/recipe-image.jpg" />
</html>""")), 'https://mock.com/recipe-image.jpg')

    def test_finds_image_when_opengraph_image_is_not_set(self):
        self.assertEqual(
            spiders.find_ketoconnect_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body="""
<html>
<div id="tve_editor">
<span class="junk">
<img class="tve_image" alt="" style="width: 400px;" src="https://mock.com/recipe-image.jpg" width="400" height="600" data-attachment-id="9282">
</span>
</div>
</html>""")), 'https://mock.com/recipe-image.jpg')

    def test_raises_error_when_image_not_found(self):
        with self.assertRaises(spiders.NoImageFound):
            spiders.find_ketoconnect_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body='<html></html>'))


class FindRuledMeImageUrlTest(unittest.TestCase):

    def test_finds_correct_image_on_simple_page(self):
        self.assertEqual(
            spiders.find_ruled_me_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body="""
<html>
  <meta property="og:image" content="https://mock.com/recipe-image.jpg" />
</html>""")), 'https://mock.com/recipe-image.jpg')

    def test_raises_error_when_image_not_found(self):
        with self.assertRaises(spiders.NoImageFound):
            spiders.find_ruled_me_image_url(
                http.TextResponse(
                    url='https://www.foo.com',
                    request=http.Request('https://www.foo.com'),
                    body='<html></html>'))
