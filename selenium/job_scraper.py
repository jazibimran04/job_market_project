import csv
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

LEVER_COMPANIES = ["rippling", "canonical", "jobgether", "lever", "pantheon-platform"]
GREENHOUSE_COMPANIES = ["duolingo", "grammarly", "deel", "reddit", "canva"]


def polite_wait(seconds=2.0):
    time.sleep(seconds)


def fetch_lever_jobs(company):
    links = []
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    logger.info(f"[Lever API] Fetching {company}")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            logger.warning(f"  {company} returned {response.status_code}")
            return links
        jobs = response.json()
        for job in jobs:
            title = job.get("text", "").strip()
            job_url = job.get("hostedUrl", "").strip()
            if title and job_url:
                links.append({
                    "company":  company.title(),
                    "platform": "Lever",
                    "title":    title,
                    "url":      job_url,
                })
                logger.info(f"  Found: {title}")
        logger.info(f"  {company} — {len(links)} jobs")
    except Exception as e:
        logger.error(f"  Error fetching {company}: {e}")
    return links


def fetch_greenhouse_jobs(company):
    links = []
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
    logger.info(f"[Greenhouse API] Fetching {company}")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            logger.warning(f"  {company} returned {response.status_code}")
            return links
        data = response.json()
        jobs = data.get("jobs", [])
        for job in jobs:
            title = job.get("title", "").strip()
            job_url = job.get("absolute_url", "").strip()
            if title and job_url:
                links.append({
                    "company":  company.title(),
                    "platform": "Greenhouse",
                    "title":    title,
                    "url":      job_url,
                })
                logger.info(f"  Found: {title}")
        logger.info(f"  {company} — {len(links)} jobs")
    except Exception as e:
        logger.error(f"  Error fetching {company}: {e}")
    return links


def collect_all_links():
    all_links = []

    for company in LEVER_COMPANIES:
        links = fetch_lever_jobs(company)
        all_links.extend(links)
        polite_wait(2)

    for company in GREENHOUSE_COMPANIES:
        links = fetch_greenhouse_jobs(company)
        all_links.extend(links)
        polite_wait(2)

    logger.info(f"Total links collected: {len(all_links)}")
    return all_links


def save_links_to_csv(links, path="data/raw/job_links.csv"):
    if not links:
        logger.warning("No links to save.")
        return
    fieldnames = ["company", "platform", "title", "url"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(links)
    logger.info(f"Saved {len(links)} links to {path}")


if __name__ == "__main__":
    links = collect_all_links()
    save_links_to_csv(links)