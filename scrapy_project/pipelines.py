import re
import json
import logging
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)

SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
    "rust", "scala", "kotlin", "swift", "r", "sql", "bash", "shell",
    "react", "vue", "angular", "html", "css", "node.js", "nodejs", "next.js",
    "graphql", "rest", "api",
    "pandas", "numpy", "spark", "hadoop", "kafka", "airflow", "dbt",
    "tensorflow", "pytorch", "scikit-learn", "machine learning", "deep learning",
    "nlp", "data pipeline", "etl",
    "aws", "gcp", "azure", "docker", "kubernetes", "ci/cd", "terraform",
    "git", "github", "linux",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "bigquery", "snowflake",
    "communication", "collaboration", "agile", "scrum",
]


class CleanFieldsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for field in adapter.field_names():
            val = adapter.get(field)
            if isinstance(val, str):
                adapter[field] = val.strip()
        etype = (adapter.get("employment_type") or "").lower()
        if any(w in etype for w in ["full", "ft"]):
            adapter["employment_type"] = "Full-time"
        elif any(w in etype for w in ["part", "pt"]):
            adapter["employment_type"] = "Part-time"
        elif "contract" in etype:
            adapter["employment_type"] = "Contract"
        elif any(w in etype for w in ["intern", "co-op"]):
            adapter["employment_type"] = "Internship"
        elif not etype:
            adapter["employment_type"] = "Not specified"
        loc = (adapter.get("location") or "").lower()
        if "remote" in loc:
            adapter["location"] = "Remote"
        elif "hybrid" in loc:
            adapter["location"] = f"Hybrid — {adapter.get('location', '')}"
        for field, default in [
            ("department",       "Not specified"),
            ("posted_date",      "Not specified"),
            ("experience_level", "Not specified"),
            ("salary",           "Not specified"),
        ]:
            if not adapter.get(field):
                adapter[field] = default
        return item


class SkillsExtractionPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        desc = (adapter.get("job_description") or "").lower()
        found = sorted({kw for kw in SKILL_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc)})
        adapter["required_skills"] = ", ".join(found) if found else "Not specified"
        return item


class DuplicateFilterPipeline:
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get("job_url", "")
        if url in self.seen_urls:
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate URL: {url}")
        self.seen_urls.add(url)
        return item


class JsonExportPipeline:
    def open_spider(self, spider):
        import os
        os.makedirs("data/final", exist_ok=True)
        self.file = open("data/final/jobs.json", "w", encoding="utf-8")
        self.file.write("[\n")
        self.first = True

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        line = json.dumps(dict(adapter), ensure_ascii=False, indent=2)
        if not self.first:
            self.file.write(",\n")
        self.file.write(line)
        self.first = False
        return item