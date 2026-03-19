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
}

FEEDS = {
    "data/final/jobs.csv":  {"format": "csv",  "overwrite": True},
    "data/final/jobs.json": {"format": "json", "overwrite": True},
}

FEED_EXPORT_FIELDS = [
    "job_title",
    "company_name",
    "location",
    "department",
    "employment_type",
    "posted_date",
    "job_url",
    "job_description",
    "required_skills",
    "experience_level",
    "salary",
]