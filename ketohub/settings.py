"""Scrapy settings for ketohub project.

http://doc.scrapy.org/en/latest/topics/settings.html
"""

BOT_NAME = 'ketohub'

SPIDER_MODULES = ['ketohub.spiders']
NEWSPIDER_MODULE = 'ketohub.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Default location for the scraped data
DOWNLOAD_ROOT = 'download_output/'
