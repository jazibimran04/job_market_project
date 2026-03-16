# Job Market Data Collection & Analysis
### Tools & Techniques for Data Science — Assignment 1
**University of Central Punjab | Faculty of IT & CS**

---

## Project Overview

This project builds an end-to-end job market data pipeline. We selected five real public company career pages, used Selenium to automate browser interaction and collect job listing URLs, then used Scrapy to crawl each URL and extract structured job data. The final dataset was analyzed to answer practical hiring trend questions such as which skills are most in demand, which companies are actively hiring, and how many entry-level positions are available.

---

## Data Sources

We selected five publicly accessible job boards across two platforms:

| Company | Platform | URL |
|---------|----------|-----|
| Reddit | Greenhouse | https://boards.greenhouse.io/reddit |
| Duolingo | Greenhouse | https://boards.greenhouse.io/duolingo |
| Grammarly | Greenhouse | https://boards.greenhouse.io/grammarly |
| Canonical | Lever | https://jobs.lever.co/canonical |
| Jobgether | Lever | https://jobs.lever.co/jobgether |

All sources are publicly accessible. No login, authentication bypass, or CAPTCHA solving was used at any point.

---

## Why Selenium and Scrapy Together

We used both tools because each serves a different purpose in the pipeline.

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
│   └── top_titles.png        
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

Step 3 — Install ChromeDriver matching your Chrome version from https://googlechromelabs.github.io/chrome-for-testing/

---

## How to Run

Step 1 — Collect job URLs using Selenium
```bash
python selenium/job_scraper.py
```
This visits all five job boards and saves URLs to data/raw/job_links.csv

Step 2 — Extract job details using Scrapy
```bash
scrapy crawl job_spider
```
This reads job_links.csv and saves results to data/final/jobs.csv and jobs.json

Step 3 — Run the analysis
```bash
python analysis/analyze_jobs.py
```
This prints a hiring trends report and saves charts to the analysis/ folder

---

## Extracted Fields

| Field | Description |
|-------|-------------|
| job_title | Exact posting title |
| company_name | Source company name |
| location | City, Remote, or Hybrid |
| department | Engineering, Product, etc. |
| employment_type | Full-time, Contract, Internship |
| posted_date | Posting date where available |
| job_url | Canonical detail page URL |
| job_description | Main description text |
| required_skills | Keywords extracted from description |
| experience_level | Entry-level, Mid, Senior (inferred) |
| salary | Where publicly listed |

---

## Key Findings

After collecting and analyzing 294 job listings:

- Most in-demand skills: Python, Go, Machine Learning, Kubernetes, Docker, AWS
- Top hiring companies: Reddit (144 roles), Duolingo (81 roles), Grammarly (69 roles)
- Entry-level positions: 159 out of 294 jobs (54.1%) were entry-level roles
- Most common titles: Software Engineer, Product Manager, Data Scientist
- Locations: Most roles were either Remote or based in San Francisco and New York

---

## Git Branching Strategy

| Branch | Purpose |
|--------|---------|
| main | Stable final version |
| develop | Integration branch |
| feature/selenium-search | Selenium automation work |
| feature/scrapy-job-parser | Scrapy spider development |
| feature/analysis-report | Analysis script |

All features were developed in dedicated branches, merged into develop, then merged into main. The submission version is tagged as v1.0.

---

## Ethical Compliance

- Only publicly accessible pages were scraped
- No login, authentication bypass, or CAPTCHA solving was used
- Polite request delays of 2 seconds between requests were applied
- ROBOTSTXT_OBEY is enabled in Scrapy settings
- No personal candidate data was collected
- All data sources are documented above for transparency