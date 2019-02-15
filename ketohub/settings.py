USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0"
BOT_NAME = 'ketohub'

SPIDER_MODULES = ['ketohub.spiders']
NEWSPIDER_MODULE = 'ketohub.spiders'

ROBOTSTXT_OBEY = False

# Default location for the scraped data
DOWNLOAD_ROOT = 'download_output/'

DOWNLOAD_DELAY = 1.0

AUTOTHROTTLE_ENABLED = True
