import csv
import re
import os
import json
import scrapy
from scrapy_project.items import JobItem


class JobSpider(scrapy.Spider):
    name = "job_spider"
    allowed_domains = [
        "api.lever.co",
        "boards-api.greenhouse.io",
        "boards.greenhouse.io",
        "job-boards.greenhouse.io",
        "careers.duolingo.com",
        "careers.grammarly.com",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "ROBOTSTXT_OBEY": False,
    }

    LEVER_COMPANIES = [
        "canonical",
        "jobgether",
        "pantheon-platform",
        "lever",
    ]

    GREENHOUSE_COMPANIES = [
        "duolingo",
        "grammarly",
        "reddit",
    ]

    def start_requests(self):
        for company in self.LEVER_COMPANIES:
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
            yield scrapy.Request(
                url,
                callback=self.parse_lever_list,
                meta={"company": company.title()},
                errback=self.handle_error,
            )

        for company in self.GREENHOUSE_COMPANIES:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
            yield scrapy.Request(
                url,
                callback=self.parse_greenhouse_list,
                meta={"company": company.title()},
                errback=self.handle_error,
            )

    def parse_lever_list(self, response):
        company = response.meta.get("company", "Unknown")
        try:
            jobs = json.loads(response.text)
        except Exception:
            self.logger.error(f"Failed to parse Lever API for {company}")
            return

        for job in jobs:
            item = JobItem()
            item["company_name"]    = company
            item["platform"]        = "Lever"
            item["job_title"]       = job.get("text", "Not specified").strip()
            item["job_url"]         = job.get("hostedUrl", "Not specified").strip()
            item["posted_date"]     = self._format_timestamp(job.get("createdAt"))
            item["employment_type"] = self._clean_field(job.get("commitment", ""))
            item["department"]      = self._clean_field(job.get("team", ""))

            categories = job.get("categories", {})
            item["location"]        = self._clean_field(
                categories.get("location", "") or job.get("workplaceType", "")
            )

            lists = job.get("lists", [])
            desc_parts = [job.get("descriptionPlain", "") or job.get("description", "")]
            for lst in lists:
                desc_parts.append(lst.get("text", ""))
                desc_parts.append(lst.get("content", ""))
            full_desc = " ".join(desc_parts)
            item["job_description"] = self._clean_text(full_desc)
            item["required_skills"] = self._extract_skills(full_desc)
            item["experience_level"]= self._detect_experience_level(
                item["job_title"] + " " + full_desc
            )
            item["salary"]          = self._extract_salary(full_desc)
            yield item

    def parse_greenhouse_list(self, response):
        company = response.meta.get("company", "Unknown")
        try:
            data = json.loads(response.text)
        except Exception:
            self.logger.error(f"Failed to parse Greenhouse API for {company}")
            return

        jobs = data.get("jobs", [])
        for job in jobs:
            item = JobItem()
            item["company_name"]    = company
            item["platform"]        = "Greenhouse"
            item["job_title"]       = job.get("title", "Not specified").strip()
            item["job_url"]         = job.get("absolute_url", "Not specified").strip()
            item["posted_date"]     = self._clean_field(job.get("updated_at", ""))[:10]

            location = job.get("location", {})
            item["location"]        = self._clean_field(
                location.get("name", "") if isinstance(location, dict) else str(location)
            )

            dept = job.get("departments", [])
            item["department"]      = dept[0].get("name", "Not specified") if dept else "Not specified"

            raw_desc = job.get("content", "") or ""
            clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
            clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
            item["job_description"] = clean_desc[:3000]
            item["required_skills"] = self._extract_skills(clean_desc)
            item["experience_level"]= self._detect_experience_level(
                item["job_title"] + " " + clean_desc
            )

            metadata = job.get("metadata", [])
            emp_type = ""
            salary = ""
            for m in metadata:
                name = (m.get("name") or "").lower()
                value = str(m.get("value") or "")
                if "employment" in name or "type" in name:
                    emp_type = value
                if "salary" in name or "compensation" in name:
                    salary = value

            item["employment_type"] = self._detect_employment_type(emp_type or item["job_title"])
            item["salary"]          = salary if salary else self._extract_salary(clean_desc)
            yield item

    @staticmethod
    def _clean_field(value):
        if not value:
            return "Not specified"
        cleaned = str(value).strip()
        return cleaned if cleaned else "Not specified"

    @staticmethod
    def _clean_text(text):
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()[:3000]

    @staticmethod
    def _format_timestamp(ts):
        if not ts:
            return "Not specified"
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(int(ts) / 1000)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return "Not specified"

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