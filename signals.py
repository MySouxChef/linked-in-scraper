from config import JOB_SEEKING_KEYWORDS


def detect_signals(profile_data):
    """Analyze a profile for job-seeking signals.

    Adds 'job_seeking_keywords_found' and 'job_seeking_score' to the profile dict.
    Returns the updated dict.
    """
    searchable_text = " ".join([
        profile_data.get("headline", ""),
        profile_data.get("about_snippet", ""),
        profile_data.get("current_title", ""),
    ]).lower()

    found_keywords = []
    score = 0

    for keyword, weight in JOB_SEEKING_KEYWORDS.items():
        if keyword.lower() in searchable_text:
            found_keywords.append(keyword)
            score += weight

    # Open to Work badge is the strongest signal
    if profile_data.get("open_to_work_badge"):
        score += 5
        if "open to work badge" not in found_keywords:
            found_keywords.append("open to work badge")

    profile_data["job_seeking_keywords_found"] = " | ".join(found_keywords) if found_keywords else ""
    profile_data["job_seeking_score"] = score

    return profile_data
