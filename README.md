# KetoHub Raw Spider

[![Build Status](https://travis-ci.org/mtlynch/ketohub_raw_spider.svg?branch=master)](https://travis-ci.org/mtlynch/ketohub_raw_spider)
[![Coverage Status](https://coveralls.io/repos/github/mtlynch/ketohub_raw_spider/badge.svg?branch=master)](https://coveralls.io/github/mtlynch/ketohub_raw_spider?branch=master)

To run the spiders:

```bash
TIMESTAMP=$(date --iso-8601=seconds | sed -r 's/://g')
OUTPUT_DIR="${HOME}/data/raw/${TIMESTAMP}/"
scrapy crawl hey-keto-mama -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl keto-size-me -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl ketoconnect -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl ketogasm -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl ketovangelist-kitchen -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl low-carb-yum -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl queen-bs -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl ruled-me -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
scrapy crawl your-friends-j -s "DOWNLOAD_ROOT=${OUTPUT_DIR}"
```
