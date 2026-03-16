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

JOB_SOURCES = [
    {
        "company":  "Reddit",
        "platform": "Greenhouse",
        "url":      "https://boards.greenhouse.io/reddit",
        "type":     "greenhouse",
    },
    {
        "company":  "Grammarly",
        "platform": "Greenhouse",
        "url":      "https://boards.greenhouse.io/grammarly",
        "type":     "greenhouse",
    },
    {
        "company":  "Duolingo",
        "platform": "Greenhouse",
        "url":      "https://boards.greenhouse.io/duolingo",
        "type":     "greenhouse",
    },
    {
        "company":  "Canonical",
        "platform": "Lever",
        "url":      "https://jobs.lever.co/canonical",
        "type":     "lever",
    },
    {
        "company":  "Jobgether",
        "platform": "Lever",
        "url":      "https://jobs.lever.co/jobgether",
        "type":     "lever",
    },
]


def make_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)


def polite_wait(seconds=2.0):
    time.sleep(seconds)


def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        polite_wait(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scrape_greenhouse(driver, source):
    links = []
    logger.info(f"[Greenhouse] Opening browser for {source['company']}")
    driver.get(source["url"])
    polite_wait(3)

    scroll_to_bottom(driver)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.opening a"))
        )
    except TimeoutException:
        logger.warning(f"Timed out waiting for jobs on {source['url']}")
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

    logger.info(f"{source['company']} — {len(links)} jobs found")
    return links


def scrape_lever(driver, source):
    links = []
    logger.info(f"[Lever] Opening browser for {source['company']}")
    driver.get(source["url"])
    polite_wait(3)

    scroll_to_bottom(driver)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.posting-title"))
        )
    except TimeoutException:
        logger.warning(f"Timed out waiting for jobs on {source['url']}")
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

    logger.info(f"{source['company']} — {len(links)} jobs found")
    return links


SCRAPERS = {
    "greenhouse": scrape_greenhouse,
    "lever":      scrape_lever,
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
                logger.error(f"Error on {source['company']}: {exc}")
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