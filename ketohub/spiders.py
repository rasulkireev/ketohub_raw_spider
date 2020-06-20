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


class DietDoctorSpider(spiders.CrawlSpider):
    name = 'diet-doctor'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['dietdoctor.com']

    # TODO(mtlynch): Make this more flexible. It's now limited to only 40 pages
    # but it should just figure out which ones are present. I've adding Rules
    # for the Previous/Next links but they don't seem to work.
    _url_prefix = ('https://www.dietdoctor.com/low-carb/recipes'
                   '?s=&st=recipe&lowcarb%5B%5D=keto&sp=')
    start_urls = [_url_prefix + str(i) for i in range(1, 40)]

    rules = [
        # Extract links for recipes,
        # e.g. /recipes/green-onion-no-chile-chicken-enchiladas
        spiders.Rule(linkextractors.LinkExtractor(
            allow=r'https://www.dietdoctor.com/recipes/'),
                     callback=callback_handler.process_callback,
                     follow=False),
    ]


class GreekGoesKetoSpider(spiders.CrawlSpider):
    name = 'greek-goes-keto'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['greekgoesketo.com']
    start_urls = ['https://www.greekgoesketo.com/category/recipes/']

    rules = [
        # Extract links for finding additional recipe pages,
        # e.g. https://www.greekgoesketo.com/category/recipes/page/1/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'https://(.+\.)greekgoesketo.com/category/recipes/page/\d+/')),
        # Extract links for recipes,
        spiders.Rule(
            linkextractors.LinkExtractor(
                restrict_css='main article'),
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
        spiders.Rule(linkextractors.LinkExtractor(
            restrict_xpaths='//div[@class="entry-content"]'),
                     callback=callback_handler.process_callback,
                     follow=False),
    ]


class KetoConnectSpider(spiders.CrawlSpider):
    name = 'ketoconnect'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketoconnect.net']
    start_urls = [
        'https://www.ketoconnect.net/main-dishes/',
        'https://www.ketoconnect.net/side-dishes/',
        'https://www.ketoconnect.net/breakfasts/',
        'https://www.ketoconnect.net/snacks/',
        'https://www.ketoconnect.net/desserts/',
        'https://www.ketoconnect.net/beverages/'
    ]

    rules = [
        # Extract links for the actual recipes
        # e.g. https://www.ketoconnect.net/recipe/spicy-cilantro-dressing/
        spiders.Rule(linkextractors.LinkExtractor(restrict_xpaths='//article'),
                     callback=callback_handler.process_callback,
                     follow=False),
    ]


class KetoDietAppSpider(spiders.SitemapSpider):
    name = 'keto-diet-app'

    sitemap_urls = [
        'https://ketodietapp.com/Blog/sitemap.axd',
    ]

    sitemap_rules = [
        ('/Blog/lchf/', 'parse_recipe'),
    ]

    def parse_recipe(self, response):
        callback_handler = CallbackHandler(
            content_saver=persist.ContentSaver(_get_download_root()))
        callback_handler.process_callback(response)


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
            linkextractors.LinkExtractor(allow=(
                r'https://www.ruled.me/keto-recipes/\w+(\-\w+)*/page/\d+/'))),

        # Extract links for the actual recipes,
        # e.g. https://www.ruled.me/easy-keto-cordon-bleu/
        spiders.Rule(linkextractors.LinkExtractor(
            allow=r'https://www.ruled.me/\w+(\-\w+)*/$',
            restrict_xpaths='//div[@id="content"]'),
                     callback=callback_handler.process_callback,
                     follow=False)
    ]


# Note: This site seems to have stopped publishing on 2018-06-15.
class KetogasmSpider(spiders.CrawlSpider):
    name = 'ketogasm'

    callback_handler = CallbackHandler(
        content_saver=persist.ContentSaver(_get_download_root()))

    allowed_domains = ['ketogasm.com']
    _url_format = ('https://ketogasm.com/recipe-index/?'
                   'fwp_recipes_filters=recipe&'
                   'fwp_paged=%d')
    start_urls = [
        (_url_format % 1),
        (_url_format % 2),
        (_url_format % 3),
        (_url_format % 4),
    ]

    rules = [
        # Extract links for recipes.
        spiders.Rule(linkextractors.LinkExtractor(
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
        spiders.Rule(linkextractors.LinkExtractor(
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
        'http://www.ketovangelistkitchen.com/indexes/recipes/appetizers/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/desserts/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/beverages/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/sides/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/snack/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/soup/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/sauces-dressings/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/casseroles/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/fat-bombs/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/dairy-free/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/kid-friendly/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/baked-goods/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/beef/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/chicken-turkey/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/chocolate/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/fish/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/pork/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/vegetables/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/nuts/',
        'http://www.ketovangelistkitchen.com/indexes/recipes/eggs/',
    ]

    rules = [
        # Extract links for recipes.
        spiders.Rule(linkextractors.LinkExtractor(
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
        spiders.Rule(linkextractors.LinkExtractor(
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
        spiders.Rule(linkextractors.LinkExtractor(
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
        spiders.Rule(linkextractors.LinkExtractor(
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
        spiders.Rule(linkextractors.LinkExtractor(
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
            linkextractors.LinkExtractor(allow=(
                r'sugarfreemom.com/recipes/category/diet/keto/page/\d+/'))),
        # Extract links for recipes.
        spiders.Rule(linkextractors.LinkExtractor(
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
        spiders.Rule(linkextractors.LinkExtractor(allow=[
            r'wholesomeyum.com/[^\/]+/$', r'wholesomeyum.com/recipes/[^\/]+/$'
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
    start_urls = ['http://yourfriendsj.com/recipe-library/']

    rules = [

        # Extract links for finding additional recipe pages,
        # e.g. http://yourfriendsj.com/tag/keto/page/2/
        spiders.Rule(
            linkextractors.LinkExtractor(
                allow=r'yourfriendsj.com/recipe-library/\?paged=\d+')),
        # Extract links for recipes,
        # e.g. http://yourfriendsj.com/recipes/easy-guacamole-recipe/
        spiders.Rule(linkextractors.LinkExtractor(
            allow=r'http://yourfriendsj.com/recipes/[^\/]*/$',
            restrict_xpaths='//article'),
                     callback=callback_handler.process_callback,
                     follow=False)
    ]
