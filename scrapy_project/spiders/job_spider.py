import csv
import re
import os
import json
import scrapy
from datetime import date
from scrapy_project.items import JobItem


class JobSpider(scrapy.Spider):
    name = "job_spider"
    allowed_domains = [
        "boards.greenhouse.io",
        "job-boards.greenhouse.io",
        "boards-api.greenhouse.io",
        "jobs.lever.co",
        "app.lever.co",
        "lever.co",
        "grnh.se",
        "greenhouse.io",
        "careers.duolingo.com",
        "careers.grammarly.com",
    ]

    links_file = os.path.join("data", "raw", "job_links.csv")

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "ROBOTSTXT_OBEY": False,
    }

    TODAY = date.today().strftime("%Y-%m-%d")

    GREENHOUSE_COMPANIES = ["duolingo", "grammarly", "reddit"]

    def start_requests(self):
        for company in self.GREENHOUSE_COMPANIES:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
            yield scrapy.Request(
                url,
                callback=self.parse_greenhouse_api,
                meta={"company": company.title()},
                errback=self.handle_error,
            )

        if not os.path.exists(self.links_file):
            self.logger.warning(f"Links file not found: {self.links_file}")
            return

        with open(self.links_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("url", "").strip()
                platform = row.get("platform", "").strip()
                company = row.get("company", "Unknown").strip()
                if not url:
                    continue
                if company.lower() in self.GREENHOUSE_COMPANIES:
                    continue
                if "lever.co" in url:
                    meta = {
                        "company":    company,
                        "platform":   platform,
                        "seed_title": row.get("title", ""),
                    }
                    yield scrapy.Request(
                        url,
                        callback=self.parse_lever,
                        meta=meta,
                        errback=self.handle_error,
                        dont_filter=True,
                    )

    def parse_greenhouse_api(self, response):
        company = response.meta.get("company", "Unknown")
        try:
            data = json.loads(response.text)
        except Exception:
            self.logger.error(f"Failed to parse Greenhouse API for {company}")
            return

        jobs = data.get("jobs", [])
        for job in jobs:
            item = JobItem()
            item["company_name"] = company
            item["platform"]     = "Greenhouse"
            item["job_title"]    = job.get("title", "").strip()
            item["job_url"]      = job.get("absolute_url", "").strip()
            item["posted_date"]  = (job.get("updated_at", "") or self.TODAY)[:10]

            location = job.get("location", {})
            item["location"] = (
                location.get("name", "Remote")
                if isinstance(location, dict)
                else str(location) or "Remote"
            )

            dept = job.get("departments", [])
            item["department"] = dept[0].get("name", "General") if dept else "General"

            raw_desc = job.get("content", "") or ""
            clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
            clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
            item["job_description"] = clean_desc[:3000]

            item["required_skills"]  = self._extract_skills(clean_desc)
            item["experience_level"] = self._detect_experience_level(
                item["job_title"] + " " + clean_desc
            )

            metadata = job.get("metadata", [])
            emp_type = ""
            salary   = ""
            for m in metadata:
                name  = (m.get("name") or "").lower()
                value = str(m.get("value") or "")
                if "employment" in name or "type" in name:
                    emp_type = value
                if "salary" in name or "compensation" in name:
                    salary = value

            item["employment_type"] = self._detect_employment_type(
                emp_type or item["job_title"]
            )
            item["salary"] = salary if salary else self._extract_salary(clean_desc)
            yield item

    def parse_lever(self, response):
        item = JobItem()
        item["job_url"]      = response.url
        item["company_name"] = response.meta.get("company", "Unknown")
        item["platform"]     = "Lever"

        item["job_title"] = (
            response.css(".posting-headline h2::text").get()
            or response.css("h2::text").get()
            or response.meta.get("seed_title", "")
        ).strip()

        item["location"] = (
            response.css(".sort-by-location::text").get()
            or response.css(".location::text").get()
            or "Remote"
        ).strip()

        item["department"] = (
            response.css(".sort-by-team::text").get()
            or response.css("[class*='department']::text").get()
            or "General"
        ).strip()

        item["employment_type"] = self._detect_employment_type(
            response.css(".sort-by-commitment::text").get() or ""
        )

        item["posted_date"] = self.TODAY

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
    def _extract_salary(text):
        patterns = [
            r"\$[\d,]+\s*[-–]\s*\$[\d,]+",
            r"\$[\d,]+k?\s*[-–]\s*\$?[\d,]+k?",
            r"[\d,]+\s*[-–]\s*[\d,]+\s*(?:USD|GBP|EUR)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "Not specified"

    SKILL_KEYWORDS = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
        "rust", "scala", "kotlin", "swift", "r", "sql", "bash", "shell",
        "react", "vue", "angular", "html", "css", "node.js", "nodejs", "next.js",
        "graphql", "rest", "api", "pandas", "numpy", "spark", "hadoop", "kafka",
        "airflow", "dbt", "tensorflow", "pytorch", "scikit-learn", "machine learning",
        "deep learning", "nlp", "data pipeline", "etl", "aws", "gcp", "azure",
        "docker", "kubernetes", "ci/cd", "terraform", "git", "github", "linux",
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "bigquery",
        "snowflake", "communication", "collaboration", "agile", "scrum",
    ]

    @classmethod
    def _extract_skills(cls, text):
        t = text.lower()
        found = sorted({kw for kw in cls.SKILL_KEYWORDS
                        if re.search(r'\b' + re.escape(kw) + r'\b', t)})
        return ", ".join(found) if found else "Not specified"

    @staticmethod
    def _detect_employment_type(hint):
        h = hint.lower()
        if any(w in h for w in ["full", "ft"]):       return "Full-time"
        if any(w in h for w in ["part", "pt"]):       return "Part-time"
        if "contract" in h:                            return "Contract"
        if any(w in h for w in ["intern", "co-op"]):  return "Internship"
        return "Full-time"

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
        return "Mid-level"

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url} — {failure.value}")