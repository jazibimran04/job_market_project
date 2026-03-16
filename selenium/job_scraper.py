"""
Selenium Job Link Collector
Visits public job boards, collects job URLs -> saves to data/raw/job_links.csv
"""

import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Target job boards
JOB_SOURCES = [
    {
        "company":  "Airtable",
        "platform": "Greenhouse",
        "url":      "https://boards.greenhouse.io/airtable",
        "type":     "greenhouse_direct",
    },
    {
        "company":  "Asana",
        "platform": "Greenhouse",
        "url":      "https://boards.greenhouse.io/asana",
        "type":     "greenhouse_direct",
    },
    {
        "company":  "Notion",
        "platform": "Lever",
        "url":      "https://www.notion.so/careers",
        "type":     "lever",
    },
    {
        "company":  "Zapier",
        "platform": "Lever",
        "url":      "https://zapier.com/jobs",
        "type":     "lever",
    },
    {
        "company":  "Figma",
        "platform": "Greenhouse",
        "url":      "https://www.figma.com/careers/",
        "type":     "greenhouse_redirect",
    },
]


def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=opts)


def polite_wait(seconds=2.0):
    time.sleep(seconds)


def scrape_greenhouse_direct(driver, source):
    links = []
    logger.info(f"[Greenhouse] Loading {source['url']}")
    driver.get(source["url"])
    polite_wait(2)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "opening"))
        )
    except TimeoutException:
        logger.warning(f"Timed out on {source['url']}")
        return links

    job_elements = driver.find_elements(By.CSS_SELECTOR, "div.opening a")
    for el in job_elements:
        href = el.get_attribute("href")
        title = el.text.strip()
        if href and title:
            links.append({
                "company":  source["company"],
                "platform": source["platform"],
                "title":    title,
                "url":      href,
            })
            logger.info(f"  Found: {title}")

    logger.info(f"{source['company']} — {len(links)} jobs collected")
    return links


def scrape_lever(driver, source):
    links = []
    logger.info(f"[Lever] Loading {source['url']}")
    driver.get(source["url"])
    polite_wait(2)

    current = driver.current_url
    if "lever.co" not in current:
        try:
            lever_link = driver.find_element(By.XPATH, "//a[contains(@href,'lever.co')]")
            lever_url = lever_link.get_attribute("href")
            logger.info(f"  Redirecting to: {lever_url}")
            driver.get(lever_url)
            polite_wait(2)
        except NoSuchElementException:
            logger.warning(f"Could not find Lever link on {source['url']}")
            return links

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "posting"))
        )
    except TimeoutException:
        logger.warning(f"Timed out on {driver.current_url}")
        return links

    postings = driver.find_elements(By.CSS_SELECTOR, "a.posting-title")
    for posting in postings:
        href = posting.get_attribute("href")
        try:
            title = posting.find_element(By.TAG_NAME, "h5").text.strip()
        except NoSuchElementException:
            title = posting.text.strip()
        if href and title:
            links.append({
                "company":  source["company"],
                "platform": source["platform"],
                "title":    title,
                "url":      href,
            })
            logger.info(f"  Found: {title}")

    logger.info(f"{source['company']} — {len(links)} jobs collected")
    return links


def scrape_greenhouse_redirect(driver, source):
    logger.info(f"[GH-Redirect] Loading {source['url']}")
    driver.get(source["url"])
    polite_wait(3)

    for text in ["view all", "open roles", "see all", "careers", "jobs"]:
        try:
            btn = driver.find_element(
                By.XPATH,
                f"//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{text}')]"
            )
            href = btn.get_attribute("href")
            if href and "greenhouse.io" in href:
                driver.get(href)
                polite_wait(2)
                break
        except NoSuchElementException:
            continue

    modified = dict(source)
    modified["url"] = driver.current_url
    return scrape_greenhouse_direct(driver, modified)


SCRAPERS = {
    "greenhouse_direct":   scrape_greenhouse_direct,
    "lever":               scrape_lever,
    "greenhouse_redirect": scrape_greenhouse_redirect,
}


def collect_all_links():
    driver = make_driver()
    all_links = []
    try:
        for source in JOB_SOURCES:
            scraper = SCRAPERS.get(source["type"])
            if not scraper:
                continue
            try:
                links = scraper(driver, source)
                all_links.extend(links)
            except Exception as exc:
                logger.error(f"Error scraping {source['company']}: {exc}")
            polite_wait(3)
    finally:
        driver.quit()

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