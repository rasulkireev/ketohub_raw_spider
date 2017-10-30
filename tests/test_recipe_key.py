import unittest

from ketohub import recipe_key


class RawContentSpiderTest(unittest.TestCase):

    def test_from_url_replaces_correct_characters(self):
        self.assertEqual(
            recipe_key.from_url('https://www.mock.com/Mikes_Chicken_Kiev/'),
            'mock-com_mikes-chicken-kiev')

    def test_from_url_handles_no_subdomain(self):
        self.assertEqual(
            recipe_key.from_url('https://mock.com/Mikes_Chicken_Kiev/'),
            'mock-com_mikes-chicken-kiev')

    def test_from_url_handles_http(self):
        self.assertEqual(
            recipe_key.from_url('http://www.mock.com/Mikes_Chicken_Kiev/'),
            'mock-com_mikes-chicken-kiev')
