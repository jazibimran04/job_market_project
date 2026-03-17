# Hiring Trends Report
---

### 1. Data Collection Summary

Job listings were collected from five publicly accessible company career boards across two platforms — Greenhouse and Lever.

| Source | Platform | Jobs Collected |
|--------|----------|----------------|
| Reddit | Greenhouse | 143 |
| Duolingo | Greenhouse | 81 |
| Grammarly | Greenhouse | 71 |
| Canonical | Lever | — |
| Lever | Lever | — |
| Total | | 295 |

---

### 2. Top Skills in Demand

Based on keyword extraction from 295 job descriptions:

- Go appeared in 81 postings — most in-demand technical skill
- Collaboration and communication dominated soft skill requirements
- Machine Learning appeared in 31 postings
- Python, Kubernetes, Java, and Docker were consistently required
- Cloud skills — AWS, GCP, Azure — appeared across multiple roles

---

### 3. Locations with Most Openings

- Remote positions led with 90 openings
- New York, NY had 33 openings — top physical location
- San Francisco, CA had 32 openings
- Pittsburgh, PA had 26 openings — strong Duolingo presence
- Berlin and London also appeared in international roles

---

### 4. Companies Posting Most Roles

- Reddit posted the most roles with 143 openings
- Duolingo followed with 81 roles
- Grammarly posted 71 roles
- Reddit dominated with roles across Engineering, Product, and Sales

---

### 5. Entry-Level and Internship Positions

- 240 out of 295 jobs (81.4%) were entry-level roles
- 4 internship positions were identified
- This indicates strong hiring activity for new graduates

---

### 6. Most Common Job Title Families

1. Software Engineer — 51 postings
2. Product Manager — 19 postings
3. Data Scientist — 11 postings
4. ML Engineer — 11 postings
5. Senior Account Executive — 4 postings

---

### 7. Employment Type Breakdown

- Full-time: 287 positions (97.3%)
- Contract: 5 positions
- Part-time: 2 positions
- Internship: 1 position

---

### 8. Methodology and Assumptions

- Selenium was used to load JavaScript-rendered job listing pages and collect detail page URLs
- Scrapy used the Greenhouse public API to extract fully structured fields
- Skills were extracted via regex matching against a predefined keyword list
- Experience level was inferred from job title and description keywords
- Salary data was available for 45 out of 295 jobs

---

### 9. Sources

- https://boards.greenhouse.io/reddit
- https://boards.greenhouse.io/duolingo
- https://boards.greenhouse.io/grammarly
- https://jobs.lever.co/canonical
- https://jobs.lever.co/lever