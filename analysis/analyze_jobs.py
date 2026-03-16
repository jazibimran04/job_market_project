import os
import re
import json
import csv
from collections import Counter

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    PLOTS = True
except ImportError:
    PLOTS = False

DATA_PATH  = os.path.join("data", "final", "jobs.csv")
OUTPUT_DIR = "analysis"


def load_jobs(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def top_skills(jobs, n=15):
    skill_counter = Counter()
    for job in jobs:
        raw = job.get("required_skills", "")
        for skill in re.split(r"[,;]+", raw):
            s = skill.strip().lower()
            if s and s != "not specified":
                skill_counter[s] += 1
    return skill_counter.most_common(n)


def top_locations(jobs, n=10):
    loc_counter = Counter()
    for job in jobs:
        loc = (job.get("location") or "Not specified").strip()
        if loc and loc.lower() not in ("", "not specified"):
            loc_counter[loc] += 1
    return loc_counter.most_common(n)


def top_companies(jobs, n=10):
    ctr = Counter(job.get("company_name", "Unknown") for job in jobs)
    return ctr.most_common(n)


def entry_level_count(jobs):
    levels = {"Entry-level": 0, "Internship": 0, "Other": 0}
    for job in jobs:
        title  = (job.get("job_title") or "").lower()
        etype  = (job.get("employment_type") or "").lower()
        elevel = (job.get("experience_level") or "").lower()
        if "intern" in etype or "intern" in title or "intern" in elevel:
            levels["Internship"] += 1
        elif "entry" in elevel or "junior" in title or "jr" in title:
            levels["Entry-level"] += 1
        else:
            levels["Other"] += 1
    return levels


def top_titles(jobs, n=10):
    def normalise(t):
        t = t.lower()
        if "data engineer"   in t: return "Data Engineer"
        if "data analyst"    in t: return "Data Analyst"
        if "data scientist"  in t: return "Data Scientist"
        if "software eng"    in t: return "Software Engineer"
        if "backend"         in t: return "Backend Engineer"
        if "frontend"        in t: return "Frontend Engineer"
        if "fullstack"       in t: return "Full-Stack Engineer"
        if "qa"              in t: return "QA / Test Engineer"
        if "product manag"   in t: return "Product Manager"
        if "devops"          in t: return "DevOps / Platform"
        if "ml"              in t: return "ML Engineer"
        if "intern"          in t: return "Intern"
        return t.title()
    ctr = Counter(normalise(job.get("job_title", "Unknown")) for job in jobs)
    return ctr.most_common(n)


def bar_chart(data, title, xlabel, filename, color="#4C72B0"):
    if not PLOTS or not data:
        return
    labels = [d[0] for d in data]
    values = [d[1] for d in data]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(labels[::-1], values[::-1], color=color)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Chart saved: {path}")


def run_analysis():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    jobs = load_jobs(DATA_PATH)
    if not jobs:
        return

    total = len(jobs)
    print("\n" + "=" * 60)
    print("        JOB MARKET ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total job records: {total}\n")

    print("── 1. TOP SKILLS ────────────────────────────────────────────")
    skills = top_skills(jobs)
    for rank, (skill, count) in enumerate(skills, 1):
        print(f"  {rank:>2}. {skill:<25} {count} postings")
    bar_chart(skills, "Top Skills in Demand", "Job Postings", "top_skills.png", "#4878CF")

    print("\n── 2. TOP LOCATIONS ─────────────────────────────────────────")
    locs = top_locations(jobs)
    for rank, (loc, count) in enumerate(locs, 1):
        print(f"  {rank:>2}. {loc:<30} {count} openings")
    bar_chart(locs, "Locations with Most Openings", "Job Count", "top_locations.png", "#6ACC65")

    print("\n── 3. TOP COMPANIES ─────────────────────────────────────────")
    companies = top_companies(jobs)
    for rank, (company, count) in enumerate(companies, 1):
        print(f"  {rank:>2}. {company:<30} {count} roles")
    bar_chart(companies, "Companies Posting Most Roles", "Job Count", "top_companies.png", "#D65F5F")

    print("\n── 4. ENTRY-LEVEL & INTERNSHIPS ─────────────────────────────")
    levels = entry_level_count(jobs)
    for level, count in levels.items():
        pct = (count / total * 100) if total else 0
        print(f"  {level:<20} {count} ({pct:.1f}%)")

    print("\n── 5. TOP JOB TITLES ────────────────────────────────────────")
    titles = top_titles(jobs)
    for rank, (title, count) in enumerate(titles, 1):
        print(f"  {rank:>2}. {title:<30} {count}")
    bar_chart(titles, "Most Common Job Titles", "Count", "top_titles.png", "#956CB4")

    summary = {
        "total_jobs":      total,
        "top_skills":      skills,
        "top_locations":   locs,
        "top_companies":   companies,
        "level_breakdown": levels,
        "top_titles":      titles,
    }
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\n  Summary saved to analysis/summary.json")
    print("=" * 60)


if __name__ == "__main__":
    run_analysis()