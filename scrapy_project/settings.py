BOT_NAME = "job_market_scraper"

SPIDER_MODULES   = ["scrapy_project.spiders"]
NEWSPIDER_MODULE = "scrapy_project.spiders"

ROBOTSTXT_OBEY           = True
DOWNLOAD_DELAY           = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS      = 4

ITEM_PIPELINES = {
    "scrapy_project.pipelines.CleanFieldsPipeline":      100,
    "scrapy_project.pipelines.SkillsExtractionPipeline": 200,
    "scrapy_project.pipelines.DuplicateFilterPipeline":  300,
    "scrapy_project.pipelines.JsonExportPipeline":       400,
}

FEEDS = {
    "data/final/jobs.csv": {
        "format":      "csv",
        "encoding":    "utf-8",
        "store_empty": False,
        "overwrite":   True,
    },
}

DEFAULT_REQUEST_HEADERS = {
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
}

LOG_LEVEL = "INFO"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"