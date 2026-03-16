import csv
import re
import os
import scrapy
from scrapy_project.items import JobItem


class JobSpider(scrapy.Spider):
    name = "job_spider"
    allowed_domains = ["boards.greenhouse.io", "jobs.lever.co", "lever.co"]
    links_file = os.path.join("data", "raw", "job_links.csv")

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def start_requests(self):
        if not os.path.exists(self.links_file):
            self.logger.error(f"Links file not found: {self.links_file}")
            return

        with open(self.links_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("url", "").strip()
                if not url:
                    continue
                meta = {
                    "company":    row.get("company", "Unknown"),
                    "platform":   row.get("platform", "Unknown"),
                    "seed_title": row.get("title", ""),
                }
                yield scrapy.Request(url, callback=self.parse_job, meta=meta, errback=self.handle_error)

    def parse_job(self, response):
        url = response.url
        if "greenhouse.io" in url:
            return self.parse_greenhouse(response)
        elif "lever.co" in url:
            return self.parse_lever(response)
        else:
            self.logger.warning(f"Unknown platform for URL: {url}")

    def parse_greenhouse(self, response):
        item = JobItem()
        item["job_url"]      = response.url
        item["company_name"] = response.meta.get("company", "Unknown")
        item["platform"]     = "Greenhouse"
        item["job_title"]    = (
            response.css("h1.app-title::text").get()
            or response.css("h1::text").get()
            or response.meta.get("seed_title", "")
        ).strip()
        item["location"] = (
            response.css(".location::text").get()
            or response.css("[class*='location']::text").get()
            or "Not specified"
        ).strip()
        item["department"] = (
            response.css(".department::text").get()
            or response.css("[class*='department']::text").get()
            or "Not specified"
        ).strip()
        item["employment_type"] = self._detect_employment_type(
            response.css("[class*='employment']::text").get() or ""
        )
        item["posted_date"] = (
            response.css("time::attr(datetime)").get()
            or response.css("[class*='date']::text").get()
            or "Not specified"
        )
        desc_parts = response.css("#content, .content, [class*='description']").css("::text").getall()
        item["job_description"] = self._clean_text(" ".join(desc_parts))
        salary_text = " ".join(response.css("[class*='salary'], [class*='compensation']::text").getall())
        item["salary"] = salary_text.strip() or "Not specified"
        item["experience_level"] = self._detect_experience_level(
            item["job_title"] + " " + item["job_description"]
        )
        item["required_skills"] = ""
        yield item

    def parse_lever(self, response):
        item = JobItem()
        item["job_url"]      = response.url
        item["company_name"] = response.meta.get("company", "Unknown")
        item["platform"]     = "Lever"
        item["job_title"]    = (
            response.css(".posting-headline h2::text").get()
            or response.css("h2::text").get()
            or response.meta.get("seed_title", "")
        ).strip()
        item["location"] = (
            response.css(".sort-by-location::text").get()
            or response.css(".location::text").get()
            or "Not specified"
        ).strip()
        item["department"] = (
            response.css(".sort-by-team::text").get()
            or response.css("[class*='department']::text").get()
            or "Not specified"
        ).strip()
        item["employment_type"] = self._detect_employment_type(
            response.css(".sort-by-commitment::text").get() or ""
        )
        item["posted_date"] = "Not specified"
        desc_parts = response.css(".section-wrapper, .posting-requirements").css("::text").getall()
        item["job_description"] = self._clean_text(" ".join(desc_parts))
        salary_text = " ".join(
            response.css("[class*='salary'], [class*='compensation']::text").getall()
        )
        item["salary"] = salary_text.strip() or "Not specified"
        item["experience_level"] = self._detect_experience_level(
            item["job_title"] + " " + item["job_description"]
        )
        item["required_skills"] = ""
        yield item

    @staticmethod
    def _clean_text(text):
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()[:3000]

    @staticmethod
    def _detect_employment_type(hint):
        h = hint.lower()
        if any(w in h for w in ["full", "ft"]):   return "Full-time"
        if any(w in h for w in ["part", "pt"]):   return "Part-time"
        if "contract" in h:                        return "Contract"
        if any(w in h for w in ["intern", "co-op"]): return "Internship"
        return "Not specified"

    @staticmethod
    def _detect_experience_level(text):
        t = text.lower()
        if any(w in t for w in ["junior", "entry", "entry-level", "jr.", "new grad", "intern"]):
            return "Entry-level"
        if any(w in t for w in ["senior", "sr.", "staff", "lead", "principal"]):
            return "Senior"
        if any(w in t for w in ["mid", "mid-level", "intermediate"]):
            return "Mid-level"
        if "manager" in t or "director" in t:
            return "Management"
        return "Not specified"

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url} — {failure.value}")