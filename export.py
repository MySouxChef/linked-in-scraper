import pandas as pd

from config import OUTPUT_FILE


COLUMNS = [
    "name",
    "headline",
    "location",
    "profile_url",
    "current_employer",
    "current_title",
    "past_employers",
    "education",
    "skills",
    "certifications",
    "about_snippet",
    "open_to_work_badge",
    "job_seeking_keywords_found",
    "job_seeking_score",
    "scraped_at",
]


def export_to_csv(profiles, filename=None):
    """Export profile data to CSV, sorted by job_seeking_score descending."""
    if not profiles:
        print("[!] No profiles to export.")
        return

    filename = filename or OUTPUT_FILE
    df = pd.DataFrame(profiles, columns=COLUMNS)

    # Fill any missing columns with empty strings
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Sort by job-seeking score (highest first)
    df = df.sort_values("job_seeking_score", ascending=False).reset_index(drop=True)

    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"\n[+] Exported {len(df)} profiles to {filename}")

    # Summary stats
    seekers = df[df["job_seeking_score"] > 0]
    print(f"[+] {len(seekers)} profiles show job-seeking signals.")
    if len(seekers) > 0:
        print(f"[+] Top score: {seekers['job_seeking_score'].max()}")
        print(f"[+] Profiles with Open to Work badge: {df['open_to_work_badge'].sum()}")
