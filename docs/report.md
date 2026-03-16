# Hiring Trends Report
## Tools & Techniques for Data Science — Assignment 1

### 1. Data Collection Summary
Job listings were collected from five publicly accessible company career boards
across two platforms (Greenhouse and Lever).

| Source   | Platform   |
|----------|------------|
| Airtable | Greenhouse |
| Asana    | Greenhouse |
| Notion   | Lever      |
| Zapier   | Lever      |
| Figma    | Greenhouse |

### 2. Top Skills in Demand
- Python appeared in the majority of data-related roles
- SQL was required in nearly all analytics and backend positions
- React and TypeScript dominated frontend roles
- AWS and GCP appeared heavily in infrastructure roles

### 3. Locations with Most Openings
- Remote positions represented the largest single category
- San Francisco and New York were the top physical locations
- Hybrid arrangements appeared frequently in mid-sized companies

### 4. Entry-Level and Internship Positions
A significant portion of listings targeted junior candidates.
Internship postings were identifiable from both employment type
and title keywords such as Intern, Co-op, and New Grad.

### 5. Most Common Job Title Families
1. Software Engineer
2. Data Engineer / Data Analyst
3. Product Manager
4. DevOps / Platform Engineer
5. QA / Test Engineer

### 6. Methodology and Assumptions
- Selenium loaded JavaScript-rendered job listing pages and collected URLs
- Scrapy crawled each URL extracting structured fields
- Skills were extracted via regex matching against a predefined keyword list
- Experience level was inferred from job title and description keywords
- Request delays of 2 to 4 seconds were applied throughout

### 7. Sources
- https://boards.greenhouse.io/airtable
- https://boards.greenhouse.io/asana
- https://www.notion.so/careers
- https://zapier.com/jobs
- https://www.figma.com/careers/