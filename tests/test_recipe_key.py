import unittest

from ketohub import recipe_key


class RawContentSpiderTest(unittest.TestCase):

    def test_from_url_replaces_correct_characters(self):
        self.assertEqual(
            recipe_key.from_url('https://www.mock.com/Mikes_Chicken_Kiev/'),
            'mock-com_mikes-chicken-kiev')
