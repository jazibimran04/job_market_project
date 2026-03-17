# Job Market Data Collection & Analysis
---

## Project Overview

This project builds an end-to-end job market data pipeline. We selected five real public company career pages, used Selenium to automate browser interaction and collect job listing URLs, then used Scrapy to crawl each URL and extract structured job data. The final dataset was analyzed to answer practical hiring trend questions such as which skills are most in demand, which companies are actively hiring, and how many entry-level positions are available.

---

## Data Sources

| Company | Platform | URL |
|---------|----------|-----|
| Reddit | Greenhouse | https://boards.greenhouse.io/reddit |
| Duolingo | Greenhouse | https://boards.greenhouse.io/duolingo |
| Grammarly | Greenhouse | https://boards.greenhouse.io/grammarly |
| Canonical | Lever | https://jobs.lever.co/canonical |
| Lever | Lever | https://jobs.lever.co/lever |

All sources are publicly accessible. No login, authentication bypass, or CAPTCHA solving was used.

---

## Why Selenium and Scrapy Together

Selenium handled the browser-side automation. It opened each careers page, waited for JavaScript-rendered content to fully load, and collected the individual job detail page URLs. This step produced the intermediate file job_links.csv.

Scrapy handled the structured extraction. It read the collected URLs from job_links.csv, visited each job detail page efficiently, extracted all required fields, cleaned the data through pipelines, and exported the final dataset to both CSV and JSON formats.

This two-tool approach reflects how scraping pipelines are built in real production systems.

---

## Project Structure
```
job_market_project/
├── selenium/
│   └── job_scraper.py
├── scrapy_project/
│   ├── spiders/
│   │   └── job_spider.py
│   ├── items.py
│   ├── pipelines.py
│   └── settings.py
├── data/
│   ├── raw/
│   │   └── job_links.csv
│   └── final/
│       ├── jobs.csv
│       └── jobs.json
├── analysis/
│   ├── analyze_jobs.py
│   ├── summary.json
│   ├── top_skills.png
│   ├── top_companies.png
│   ├── top_titles.png
│   ├── top_locations.png
│   └── experience_levels.png
├── docs/
│   └── report.md
├── requirements.txt
├── scrapy.cfg
├── .gitignore
└── README.md
```

---

## Setup Instructions

Step 1 — Clone the repository
```bash
git clone https://github.com/jazibimran04/job_market_project.git
cd job_market_project
```

Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

Step 1 — Collect job URLs using Selenium
```bash
python selenium/job_scraper.py
```

Step 2 — Extract job details using Scrapy
```bash
scrapy crawl job_spider
```

Step 3 — Run the analysis
```bash
python analysis/analyze_jobs.py
```

---

## Extracted Fields

| Field | Description |
|-------|-------------|
| job_title | Exact posting title |
| company_name | Source company name |
| location | City, Remote, or Hybrid |
| department | Engineering, Product, Finance etc. |
| employment_type | Full-time, Contract, Internship |
| posted_date | Posting date |
| job_url | Canonical detail page URL |
| job_description | Clean description text |
| required_skills | Keywords extracted from description |
| experience_level | Entry-level, Mid, Senior, Management |
| salary | Where publicly listed |

---

## Key Findings

After collecting and analyzing 295 job listings:

- Most in-demand skills: Go, Collaboration, Machine Learning, Python, Kubernetes
- Top hiring companies: Reddit (143 roles), Duolingo (81 roles), Grammarly (71 roles)
- Top locations: Remote (90), New York NY (33), San Francisco CA (32), Pittsburgh PA (26)
- Entry-level positions: 240 out of 295 jobs (81.4%)
- Most common titles: Software Engineer (51), Product Manager (19), Data Scientist (11)
- Employment types: Full-time (287), Contract (5), Part-time (2), Internship (1)

---

## Git Branching Strategy

| Branch | Purpose |
|--------|---------|
| main | Stable final version |
| develop | Integration branch |
| feature/selenium-search | Selenium automation |
| feature/scrapy-job-parser | Scrapy spider |
| feature/analysis-report | Analysis script |

All features were developed in dedicated branches, merged into develop, then merged into main. Tagged as v1.0.

---

## Ethical Compliance

- Only publicly accessible pages were scraped
- No login, authentication bypass, or CAPTCHA solving was used
- Polite request delays applied throughout
- ROBOTSTXT_OBEY enabled in Scrapy settings
- No personal candidate data collected