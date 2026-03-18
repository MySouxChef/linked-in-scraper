# LinkedIn Radiologist Job-Seeker Scraper

A Python tool that scrapes LinkedIn to find radiologists who are actively looking for jobs. It uses browser automation with [undetected-chromedriver](https://github.com/ultrafunkula/undetected-chromedriver) to bypass bot detection, collects profile data, detects job-seeking signals (Open to Work badge, keywords), and exports scored results to CSV.

## Quick Start (Step by Step)

### Step 1: Make sure you have the prerequisites

- **Python 3.9+** — download from [python.org](https://www.python.org/downloads/) if you don't have it
- **Google Chrome** — must be installed and up to date
- A **throwaway LinkedIn account** (do not use your primary account — scraping may trigger account restrictions)

### Step 2: Clone the repository

Open a terminal (Command Prompt, PowerShell, or Git Bash) and run:

```bash
git clone https://github.com/MySouxChef/linked-in-scraper.git
cd linked-in-scraper
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

This installs: `selenium`, `undetected-chromedriver`, `python-dotenv`, `pandas`, and `winotify` (for Windows notifications).

### Step 4: Add your LinkedIn credentials

```bash
cp .env.example .env
```

Open the `.env` file in any text editor and replace the placeholders:

```
LINKEDIN_EMAIL=your-throwaway-email@example.com
LINKEDIN_PASSWORD=your-password-here
```

**Important:** Never commit your `.env` file. It is already in `.gitignore`.

### Step 5: Run the scraper

```bash
python main.py
```

That's it. The scraper will log in, search for radiologist profiles, scrape them, and export the results. You'll get a **Windows notification** when it finishes or if something goes wrong.

## Running Options

| Command | What it does |
|---|---|
| `python main.py` | Run the scraper in headless mode (no browser window) |
| `python main.py --no-headless` | Run with a visible browser — useful for debugging or completing CAPTCHAs |

### First run tip

On your first run, LinkedIn may ask for a CAPTCHA or email verification. If this happens, run with `--no-headless` so you can complete the challenge in the visible browser. After that, cookies are saved and future runs (including headless) won't need it again.

## What happens when you run it

The scraper runs in three phases:

1. **Search** (~15–30 min) — Queries LinkedIn using 8 keyword variations (e.g. "radiologist", "diagnostic radiologist", "interventional radiologist") and collects profile URLs from up to 10 pages per query
2. **Scrape** (~30–60 min) — Visits up to 80 profiles per session, extracting name, headline, employer, education, skills, and job-seeking signals
3. **Export** — Writes everything to `radiologists_job_seekers.csv`, sorted by job-seeking score

**Total time per run: ~45–90 minutes** (delays are intentionally slow to avoid detection).

### Expected results

| | Estimate |
|---|---|
| Profiles found per run | 200–500 unique URLs collected from search |
| Profiles scraped per run | Up to 80 (session limit to avoid detection) |
| Full coverage | 3–6 runs to scrape all collected profiles |

### Resuming an interrupted scrape

Progress is automatically saved to `scrape_progress.json`. If a run is interrupted (Ctrl+C, crash, or session limit), just run `python main.py` again — it picks up where it left off.

To start completely fresh:

```bash
rm scrape_progress.json
```

## Notifications

You'll receive a **Windows toast notification** for these events:

| Event | Notification |
|---|---|
| Scrape complete | Shows how many profiles were scraped and how many show job-seeking signals |
| Interrupted (Ctrl+C) | Confirms progress was saved and tells you to run again to resume |
| Error / crash | Shows the error message |
| Login failed | Alerts you to check your credentials |

Notifications appear even when the terminal is in the background, so you can start the scraper and do other work.

## Output

Results are saved to `radiologists_job_seekers.csv` with these columns:

| Column | Description |
|---|---|
| `name` | Full name |
| `headline` | LinkedIn headline |
| `location` | Geographic location |
| `profile_url` | Direct link to profile |
| `current_employer` | Current company |
| `current_title` | Current job title |
| `past_employers` | Previous positions (pipe-separated) |
| `education` | Schools and degrees (pipe-separated) |
| `skills` | Listed skills (pipe-separated) |
| `certifications` | Licenses and certifications (pipe-separated) |
| `about_snippet` | First 500 chars of About section |
| `open_to_work_badge` | `True` if Open to Work badge detected |
| `job_seeking_keywords_found` | Which job-seeking keywords were found |
| `job_seeking_score` | Weighted score — higher means more likely job-seeking |
| `scraped_at` | Timestamp of when the profile was scraped |

Profiles are sorted by `job_seeking_score` in descending order, so the most likely job seekers appear first.

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---|---|---|
| `SEARCH_QUERIES` | 8 radiologist variations | LinkedIn search keywords |
| `PAGE_DELAY` | 5–15 seconds | Delay between profile visits |
| `ACTION_DELAY` | 2–5 seconds | Delay between actions on a page |
| `MAX_PAGES_PER_QUERY` | 10 | Search result pages per query (LinkedIn free cap) |
| `MAX_PROFILES_PER_SESSION` | 80 | Profiles scraped per run to avoid detection |
| `JOB_SEEKING_KEYWORDS` | 11 keywords with weights | Keywords and their scores for signal detection |

### Job-Seeking Signal Scoring

Each keyword found in a profile's headline or about section adds to their score:

| Signal | Weight |
|---|---|
| Open to Work badge | +5 |
| "open to work", "open to opportunities", "actively searching", "#opentowork" | +3 |
| "seeking", "looking for", "in transition", "exploring opportunities", "between roles", "job search" | +2 |
| "available" | +1 |

## Anti-Detection Features

- **undetected-chromedriver** patches Chrome to avoid Selenium detection
- **Random delays** between all actions to mimic human browsing
- **Human-like scrolling** with randomized scroll distances and pauses
- **Character-by-character typing** for login fields with random keystroke delays
- **Cookie persistence** to avoid repeated logins (`linkedin_cookies.pkl`)
- **Session limits** capping profiles per run at 80

## Troubleshooting

### Security challenge / CAPTCHA on login

LinkedIn may require verification on new logins. Run with `--no-headless` to complete the challenge manually in the visible browser. After a successful login, cookies are saved so subsequent runs won't need to re-authenticate.

### "No profiles to scrape"

- Verify your LinkedIn credentials in `.env` are correct
- Your account may be restricted — try logging in manually via browser
- LinkedIn may have changed their page structure — check for updates to this repo

### Scraper stops finding results early

Free LinkedIn accounts are limited to ~100 results per search query (10 pages x 10 results). The scraper uses multiple keyword variations to expand coverage, but total yield is typically 200–500 unique profiles.

### Chrome driver errors

Make sure Google Chrome is installed and up to date. `undetected-chromedriver` automatically downloads the matching driver version.

## Project Structure

```
linked-in-scraper/
├── main.py              # Entry point — orchestrates the scrape
├── config.py            # Settings (credentials, delays, search terms)
├── browser.py           # Browser setup + LinkedIn login
├── scraper.py           # Search + profile URL collection
├── parser.py            # Extract structured data from profile pages
├── signals.py           # Detect job-seeking signals
├── export.py            # Export results to CSV
├── requirements.txt     # Python dependencies
├── .env.example         # Credential template
└── .gitignore           # Excludes .env, cookies, output files
```

## Disclaimer

This tool is for educational and research purposes. Scraping LinkedIn may violate their Terms of Service. Use a throwaway account and respect rate limits. The authors are not responsible for any account restrictions or legal consequences resulting from use of this tool.
