import scrapy


class JobItem(scrapy.Item):
    job_title        = scrapy.Field()
    company_name     = scrapy.Field()
    location         = scrapy.Field()
    department       = scrapy.Field()
    employment_type  = scrapy.Field()
    posted_date      = scrapy.Field()
    job_url          = scrapy.Field()
    job_description  = scrapy.Field()
    required_skills  = scrapy.Field()
    experience_level = scrapy.Field()
    salary           = scrapy.Field()