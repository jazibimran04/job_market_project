# Job Market Data Collection & Analysis

## Project Overview
An end-to-end pipeline that collects job listings from public job boards,
extracts structured data, and generates hiring insights.

## Data Sources
- Airtable (Greenhouse) — https://boards.greenhouse.io/airtable
- Asana (Greenhouse) — https://boards.greenhouse.io/asana
- Notion (Lever) — https://www.notion.so/careers
- Zapier (Lever) — https://zapier.com/jobs
- Figma (Greenhouse) — https://www.figma.com/careers/

## How to Run
1. Run Selenium: `python selenium/job_scraper.py`
2. Run Scrapy: `scrapy crawl job_spider`
3. Run Analysis: `python analysis/analyze_jobs.py`

## Ethical Compliance
- Only public pages scraped
- No login or CAPTCHA bypass
- Polite delays between requests