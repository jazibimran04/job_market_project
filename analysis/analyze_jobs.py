import os
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_PATH  = os.path.join("data", "final", "jobs.csv")
OUTPUT_DIR = "analysis"


def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"File not found: {DATA_PATH}")
        return None
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} job records")
    return df


def top_skills(df, n=15):
    skills = (
        df["required_skills"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .str.lower()
        .replace("not specified", pd.NA)
        .dropna()
    )
    return skills.value_counts().head(n)


def top_locations(df, n=10):
    locs = (
        df["location"]
        .dropna()
        .str.strip()
        .replace("Not specified", pd.NA)
        .dropna()
    )
    return locs.value_counts().head(n)


def top_companies(df, n=10):
    return df["company_name"].value_counts().head(n)


def entry_level_count(df):
    total = len(df)
    internship = df[
        df["employment_type"].str.lower().str.contains("intern", na=False) |
        df["job_title"].str.lower().str.contains("intern", na=False)
    ].shape[0]
    entry = df[
        df["experience_level"].str.lower().str.contains("entry", na=False) |
        df["job_title"].str.lower().str.contains("junior|jr\\.|new grad", na=False, regex=True)
    ].shape[0]
    other = total - internship - entry
    return pd.Series({
        "Internship":  internship,
        "Entry-level": entry,
        "Other":       other,
    })


def top_titles(df, n=10):
    def normalise(t):
        t = str(t).lower()
        if "data engineer"  in t: return "Data Engineer"
        if "data analyst"   in t: return "Data Analyst"
        if "data scientist" in t: return "Data Scientist"
        if "software eng"   in t: return "Software Engineer"
        if "backend"        in t: return "Backend Engineer"
        if "frontend"       in t: return "Frontend Engineer"
        if "fullstack"      in t or "full stack" in t: return "Full-Stack Engineer"
        if "qa"             in t: return "QA / Test Engineer"
        if "product manag"  in t: return "Product Manager"
        if "devops"         in t: return "DevOps / Platform"
        if "ml"             in t or "machine learning" in t: return "ML Engineer"
        if "intern"         in t: return "Intern"
        return t.title()
    return df["job_title"].apply(normalise).value_counts().head(n)


def bar_chart(series, title, xlabel, filename, color="#4C72B0"):
    if series.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    series[::-1].plot(kind="barh", ax=ax, color=color)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"  Chart saved: {path}")


def run_analysis():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()
    if df is None:
        return

    total = len(df)
    print("\n" + "=" * 60)
    print("        JOB MARKET ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total job records: {total}\n")

    print("── 1. TOP SKILLS ────────────────────────────────────────────")
    skills = top_skills(df)
    print(skills.to_string())
    bar_chart(skills, "Top Skills in Demand", "Job Postings", "top_skills.png", "#4878CF")

    print("\n── 2. TOP LOCATIONS ─────────────────────────────────────────")
    locs = top_locations(df)
    if locs.empty:
        print("  No location data available")
    else:
        print(locs.to_string())
    bar_chart(locs, "Locations with Most Openings", "Job Count", "top_locations.png", "#6ACC65")

    print("\n── 3. TOP COMPANIES ─────────────────────────────────────────")
    companies = top_companies(df)
    print(companies.to_string())
    bar_chart(companies, "Companies Posting Most Roles", "Job Count", "top_companies.png", "#D65F5F")

    print("\n── 4. ENTRY-LEVEL & INTERNSHIPS ─────────────────────────────")
    levels = entry_level_count(df)
    for level, count in levels.items():
        pct = count / total * 100
        print(f"  {level:<20} {count} ({pct:.1f}%)")

    print("\n── 5. TOP JOB TITLES ────────────────────────────────────────")
    titles = top_titles(df)
    print(titles.to_string())
    bar_chart(titles, "Most Common Job Titles", "Count", "top_titles.png", "#956CB4")

    print("\n── 6. EMPLOYMENT TYPE BREAKDOWN ─────────────────────────────")
    emp = df["employment_type"].value_counts()
    print(emp.to_string())

    print("\n── 7. EXPERIENCE LEVEL BREAKDOWN ────────────────────────────")
    exp = df["experience_level"].value_counts()
    print(exp.to_string())
    bar_chart(exp, "Experience Level Distribution", "Count", "experience_levels.png", "#56AEC4")

    summary = {
        "total_jobs":        total,
        "top_skills":        skills.to_dict(),
        "top_locations":     locs.to_dict(),
        "top_companies":     companies.to_dict(),
        "level_breakdown":   levels.to_dict(),
        "top_titles":        titles.to_dict(),
        "employment_types":  emp.to_dict(),
        "experience_levels": exp.to_dict(),
    }
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\n  Summary saved to analysis/summary.json")
    print("=" * 60)


if __name__ == "__main__":
    run_analysis()