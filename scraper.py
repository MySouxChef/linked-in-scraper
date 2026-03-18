import time
import random
import json
import os
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import (
    SEARCH_QUERIES,
    PAGE_DELAY,
    ACTION_DELAY,
    SCROLL_DELAY,
    MAX_PAGES_PER_QUERY,
    MAX_PROFILES_PER_SESSION,
    PROGRESS_FILE,
)


def _human_scroll(driver):
    """Scroll down the page in a human-like pattern."""
    scroll_pause = random.uniform(*SCROLL_DELAY)
    scroll_amount = random.randint(300, 700)
    for _ in range(random.randint(2, 5)):
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(scroll_pause)
        scroll_amount = random.randint(200, 600)


def _build_search_url(query, page=1):
    """Build a LinkedIn people search URL."""
    encoded = quote_plus(query)
    return f"https://www.linkedin.com/search/results/people/?keywords={encoded}&page={page}"


def save_progress(scraped_urls, pending_urls):
    """Save scraping progress so we can resume after interruption."""
    data = {
        "scraped": list(scraped_urls),
        "pending": list(pending_urls),
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)
    print(f"[+] Progress saved: {len(scraped_urls)} scraped, {len(pending_urls)} pending.")


def load_progress():
    """Load previous progress if available."""
    if not os.path.exists(PROGRESS_FILE):
        return set(), []
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        scraped = set(data.get("scraped", []))
        pending = list(data.get("pending", []))
        print(f"[+] Resumed progress: {len(scraped)} already scraped, {len(pending)} pending.")
        return scraped, pending
    except Exception:
        return set(), []


def collect_profile_urls(driver):
    """Run all search queries and collect unique profile URLs."""
    scraped_urls, pending_urls = load_progress()
    if pending_urls:
        print(f"[*] Resuming with {len(pending_urls)} pending URLs.")
        return scraped_urls, pending_urls

    all_urls = set()
    for query in SEARCH_QUERIES:
        print(f"\n[*] Searching: '{query}'")
        for page in range(1, MAX_PAGES_PER_QUERY + 1):
            url = _build_search_url(query, page)
            print(f"  [*] Page {page}...")

            try:
                driver.get(url)
                time.sleep(random.uniform(*ACTION_DELAY))
                _human_scroll(driver)

                # Wait for results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".reusable-search__result-container"))
                )

                # Extract profile links
                links = driver.find_elements(
                    By.CSS_SELECTOR,
                    ".reusable-search__result-container a.app-aware-link[href*='/in/']"
                )
                page_urls = set()
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/in/" in href:
                        # Normalize URL — strip query params
                        clean = href.split("?")[0].rstrip("/")
                        page_urls.add(clean)

                new_count = len(page_urls - all_urls)
                all_urls.update(page_urls)
                print(f"    Found {len(page_urls)} profiles ({new_count} new). Total: {len(all_urls)}")

                if not page_urls:
                    print(f"    No results on page {page}, moving to next query.")
                    break

            except TimeoutException:
                print(f"    [!] Page {page} timed out, moving on.")
                break
            except Exception as e:
                print(f"    [!] Error on page {page}: {e}")
                break

            time.sleep(random.uniform(*PAGE_DELAY))

    # Remove already-scraped URLs
    pending = list(all_urls - scraped_urls)
    print(f"\n[+] Collected {len(all_urls)} total unique profiles, {len(pending)} to scrape.")

    if len(pending) > MAX_PROFILES_PER_SESSION:
        print(f"[*] Limiting to {MAX_PROFILES_PER_SESSION} profiles this session.")
        pending = pending[:MAX_PROFILES_PER_SESSION]

    save_progress(scraped_urls, pending)
    return scraped_urls, pending


def scrape_profile(driver, profile_url):
    """Visit a profile page and return the page source for parsing."""
    try:
        driver.get(profile_url)
        time.sleep(random.uniform(*ACTION_DELAY))
        _human_scroll(driver)

        # Wait for profile to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card, .scaffold-layout__main"))
        )

        # Scroll to load lazy sections
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(random.uniform(*SCROLL_DELAY))

        return driver.page_source

    except TimeoutException:
        print(f"  [!] Profile timed out: {profile_url}")
        return None
    except Exception as e:
        print(f"  [!] Error scraping {profile_url}: {e}")
        return None
