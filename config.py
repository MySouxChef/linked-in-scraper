import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Search queries — multiple variations to maximize coverage
SEARCH_QUERIES = [
    "radiologist",
    "diagnostic radiologist",
    "interventional radiologist",
    "radiology physician",
    "neuroradiologist",
    "musculoskeletal radiologist",
    "radiology attending",
    "radiologist open to work",
]

# Delay ranges (seconds) — mimics human browsing patterns
PAGE_DELAY = (5, 15)       # Between profile page visits
ACTION_DELAY = (2, 5)      # Between actions on a single page
SCROLL_DELAY = (1, 3)      # Between scroll actions

# Scraping limits
MAX_PAGES_PER_QUERY = 10   # LinkedIn free caps at ~10 pages
MAX_PROFILES_PER_SESSION = 80  # Stay under detection threshold

# Job-seeking keywords and their weights
JOB_SEEKING_KEYWORDS = {
    "open to work": 3,
    "seeking": 2,
    "looking for": 2,
    "open to opportunities": 3,
    "actively searching": 3,
    "available": 1,
    "in transition": 2,
    "exploring opportunities": 2,
    "between roles": 2,
    "job search": 2,
    "#opentowork": 3,
}

# Output
OUTPUT_FILE = "radiologists_job_seekers.csv"
COOKIE_FILE = "linkedin_cookies.pkl"
PROGRESS_FILE = "scrape_progress.json"
