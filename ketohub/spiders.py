from scrapy import conf
from scrapy import linkextractors
from scrapy import spiders

import persist
import recipe_key


class Error(Exception):
    """Base Error class."""
    pass


class MissingDownloadDirectory(Error):
    """Error raised when the download directory is not defined."""
    pass


def _get_download_root():
    download_root = conf.settings.get('DOWNLOAD_ROOT')
    if not download_root:
        raise MissingDownloadDirectory(
            'Make sure you\'re providing a download directory.')
    return download_root


class CallbackHandler(object):

    def __init__(self, content_saver):
        self._content_saver = content_saver

    def process_callback(self, response):
        key = recipe_key.from_url(response.url)
        self._content_saver.save_metadata(
            key, {
                'url': response.url,
                'referer': response.request.headers['Referer'],
            })
        self._content_saver.save_recipe_html(key, response.text.encode('utf8'))


class GreekGoesKetoSpider(spiders.CrawlSpider):
    name = 'greek-goes-keto'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['greekgoesketo.com']
    start_urls = ['https://greekgoesketo.com/category/recipes/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://greekgoesketo.com/category/recipes/page/1/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://greekgoesketo.com/category/recipes/page/\d+/')),
        # Extract links for recipes,
        # e.g. https://www.heyketomama.com/ten-minute-keto-nachos/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://greekgoesketo.com/\d{4}/\d{2}/\d{2}/.+/',
                restrict_xpaths='//div[@class="content-block"]'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class HeyKetoMamaSpider(spiders.CrawlSpider):
    name = 'hey-keto-mama'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['heyketomama.com']
    start_urls = ['https://www.heyketomama.com/category/recipes/page/1/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://www.heyketomama.com/category/recipes/page/6/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.heyketomama.com/category/recipes/page/\d+/')
        ),
        # Extract links for recipes,
        # e.g. https://www.heyketomama.com/ten-minute-keto-nachos/
        spiders.Rule(
            linkextractors.LinkExtractor(
                restrict_xpaths='//div[@class="entry-content"]'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class KetoConnectSpider(spiders.CrawlSpider):
    name = 'ketoconnect'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketoconnect.net']
    start_urls = ['https://www.ketoconnect.net/recipes/']

    rules = [
        # Extract links for food category pages,
        # e.g. https://ketoconnect.net/desserts/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ketoconnect.net/\w+(-\w+)*/$',
                restrict_xpaths=
                '//div[@id="tve_editor"]//span[@class="tve_custom_font_size rft"]'
            )),

        # Extract links for the actual recipes
        # e.g. https://www.ketoconnect.net/recipe/spicy-cilantro-dressing/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ketoconnect.net/recipe/\w+(-\w+)*/$',
                restrict_xpaths='//div[@class="tve_post tve_post_width_4"]'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class RuledMeSpider(spiders.CrawlSpider):
    name = 'ruled-me'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ruled.me']
    start_urls = ['https://www.ruled.me/keto-recipes/']

    rules = [
        # Extract links for food category pages,
        # e.g. https://www.ruled.me/keto-recipes/breakfast/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ruled.me/keto-recipes/\w+(\-\w+)*/$',
                restrict_xpaths='//div[@class="r-list"]')),

        # Extract links for finding additional pages within food category pages,
        # e.g. https://www.ruled.me/keto-recipes/dinner/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=(
                    r'https://www.ruled.me/keto-recipes/\w+(\-\w+)*/page/\d+/'))
        ),

        # Extract links for the actual recipes,
        # e.g. https://www.ruled.me/easy-keto-cordon-bleu/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ruled.me/\w+(\-\w+)*/$',
                restrict_xpaths='//div[@id="content"]'),
            callback=callback_handler.process_callback,
            follow=False)
    ]


class KetogasmSpider(spiders.CrawlSpider):
    name = 'ketogasm'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketogasm.com']
    start_urls = [
        'https://ketogasm.com/recipe-index/?fwp_recipes_filters=recipe'
    ]

    rules = [
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://ketogasm.com/.*/$',
                restrict_xpaths='//div[@id="recipes-grid"]'),
            callback=callback_handler.process_callback,
            follow=False)
    ]


class KetoSizeMe(spiders.CrawlSpider):
    name = 'keto-size-me'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketosizeme.com']
    start_urls = ['https://ketosizeme.com/category/ketogenic-diet-recipes/']

    rules = [

        # Extract links for finding additional pages within recipe index,
        # e.g. https://ketosizeme.com/category/ketogenic-diet-recipes/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=
                r'https://ketosizeme.com/category/ketogenic-diet-recipes/page/\d+/'
            )),

        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://ketosizeme.com/.+/$', restrict_xpaths='//main'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class KetovangelistKitchen(spiders.CrawlSpider):
    name = 'ketovangelist-kitchen'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketovangelistkitchen.com']
    # Organize start URLs in descending order of category strength (e.g. muffins
    # should be categorized as "snack" not "eggs".
    start_urls = [
        'http://www.ketovangelistkitchen.com/category/appetizers/',
        'http://www.ketovangelistkitchen.com/category/sides/',
        'http://www.ketovangelistkitchen.com/category/snack/',
        'http://www.ketovangelistkitchen.com/category/soup/',
        'http://www.ketovangelistkitchen.com/category/sauces-dressings/',
        'http://www.ketovangelistkitchen.com/category/fat-bombs/',
        'http://www.ketovangelistkitchen.com/category/baked-goods/',
        'http://www.ketovangelistkitchen.com/category/beef/',
        'http://www.ketovangelistkitchen.com/category/chicken-turkey/',
        'http://www.ketovangelistkitchen.com/category/chocolate/',
        'http://www.ketovangelistkitchen.com/category/fish/',
        'http://www.ketovangelistkitchen.com/category/pork/',
        'http://www.ketovangelistkitchen.com/category/nuts/',
        'http://www.ketovangelistkitchen.com/category/eggs/',
    ]

    rules = [
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'http://(www.)?ketovangelistkitchen.com/.+/$',
                restrict_xpaths='//div[@class="entry-content"]'),
            callback=callback_handler.process_callback,
            follow=False)
    ]


class Ketovale(spiders.CrawlSpider):
    name = 'ketovale'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketovale.com']
    start_urls = ['https://www.ketovale.com/category/recipes/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://www.ketovale.com/category/recipes/page/3/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ketovale.com/category/recipes/page/\d+/')),
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://www.ketovale.com/recipe/.*/$',
                restrict_xpaths='//h2[@class="entry-title"]'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class LowCarbYum(spiders.CrawlSpider):
    name = 'low-carb-yum'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['lowcarbyum.com']
    start_urls = ['https://lowcarbyum.com/recipes/']

    rules = [
        # Extract links for food category pages,
        # e.g. https://lowcarbyum.com/category/desserts/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://lowcarbyum.com/category/',
                deny=r'https://lowcarbyum.com/category/((reviews)|(articles))')
        ),
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://lowcarbyum.com/.+/$',
                restrict_xpaths='//header[@class="entry-header"]'),
            callback=callback_handler.process_callback,
            follow=False)
    ]


class QueenBs(spiders.CrawlSpider):
    name = 'queen-bs'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['queenbsincredibleedibles.com']
    start_urls = ['http://queenbsincredibleedibles.com/category/keto/page/1/']

    rules = [
        # Extract links for finding additional keto recipe pages,
        # e.g. http://queenbsincredibleedibles.com/category/keto/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=
                r'http://queenbsincredibleedibles.com/category/keto/page/\d+/')
        ),

        # Extract links for recipes,
        # e.g. http://queenbsincredibleedibles.com/creamy-coconut-kale-sausage-soup/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'http://queenbsincredibleedibles.com/.*/$',
                deny=r'(category\/)|(ive-fallen-in-love-with-keto)'),
            callback=callback_handler.process_callback,
            follow=False)
    ]


class SkinnyTaste(spiders.CrawlSpider):
    name = 'skinny-taste'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['skinnytaste.com']
    start_urls = ['https://www.skinnytaste.com/recipes/keto/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://www.skinnytaste.com/recipes/keto/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'skinnytaste.com/recipes/keto/page/\d+/')),
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=[
                    r'skinnytaste.com/[^\/]+/$',
                ],
                restrict_xpaths='//div[@class="archives"]'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class SugarFreeMom(spiders.CrawlSpider):
    name = 'sugar-free-mom'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['sugarfreemom.com']
    start_urls = ['https://www.sugarfreemom.com/recipes/category/diet/keto/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://www.sugarfreemom.com/recipes/category/diet/keto/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=(
                    r'sugarfreemom.com/recipes/category/diet/keto/page/\d+/'))),
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'sugarfreemom.com/recipes/[^\/]+/$',
                restrict_xpaths='//main'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class WholesomeYum(spiders.CrawlSpider):
    name = 'wholesome-yum'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['wholesomeyum.com']
    start_urls = ['https://www.wholesomeyum.com/tag/keto/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://www.wholesomeyum.com/tag/keto/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'wholesomeyum.com/tag/keto/page/\d+/')),
        # Extract links for recipes.
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=[
                    r'wholesomeyum.com/[^\/]+/$',
                    r'wholesomeyum.com/recipes/[^\/]+/$'
                ],
                restrict_xpaths='//main'),
            callback=callback_handler.process_callback,
            follow=False),
    ]


class YourFriendsJ(spiders.CrawlSpider):
    name = 'your-friends-j'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['yourfriendsj.com']
    start_urls = ['http://yourfriendsj.com/recipes/']

    rules = [
        # Extract links for recipes,
        # e.g. http://yourfriendsj.com/easy-guacamole-recipe/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'http://yourfriendsj.com/recipes/[^\/]*/$',
                restrict_xpaths='//article'),
            callback=callback_handler.process_callback,
            follow=False)
    ]
