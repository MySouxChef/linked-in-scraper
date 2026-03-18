#!/usr/bin/env python3
"""LinkedIn Radiologist Job-Seeker Scraper — Main Entry Point."""

import sys
import time
import random
import json

from config import PAGE_DELAY, PROGRESS_FILE, MAX_PROFILES_PER_SESSION
from browser import create_browser, login
from scraper import collect_profile_urls, scrape_profile, save_progress
from parser import parse_profile
from signals import detect_signals
from export import export_to_csv


def main():
    print("=" * 60)
    print("  LinkedIn Radiologist Job-Seeker Scraper")
    print("=" * 60)

    # Initialize browser
    headless = "--no-headless" not in sys.argv
    if not headless:
        print("[*] Running in visible browser mode.")
    print("[*] Starting browser...")
    driver = create_browser(headless=headless)

    try:
        # Login
        if not login(driver):
            print("[!] Could not log in. Exiting.")
            return

        # Collect profile URLs from search
        print("\n[*] Phase 1: Collecting profile URLs from search...")
        scraped_urls, pending_urls = collect_profile_urls(driver)

        if not pending_urls:
            print("[!] No profiles to scrape. Try different search terms or check your account.")
            return

        # Scrape individual profiles
        print(f"\n[*] Phase 2: Scraping {len(pending_urls)} profiles...")
        profiles = []
        for i, url in enumerate(pending_urls):
            if i >= MAX_PROFILES_PER_SESSION:
                print(f"[*] Session limit reached ({MAX_PROFILES_PER_SESSION}). Saving progress.")
                break

            print(f"  [{i + 1}/{len(pending_urls)}] {url}")

            page_source = scrape_profile(driver, url)
            if page_source:
                data = parse_profile(driver, url)
                data = detect_signals(data)
                profiles.append(data)
                scraped_urls.add(url)

                if data["job_seeking_score"] > 0:
                    print(f"    -> Job seeker signal! Score: {data['job_seeking_score']} "
                          f"({data['job_seeking_keywords_found']})")

            # Save progress periodically
            if (i + 1) % 10 == 0:
                remaining = [u for u in pending_urls[i + 1:] if u not in scraped_urls]
                save_progress(scraped_urls, remaining)

            # Random delay between profiles
            time.sleep(random.uniform(*PAGE_DELAY))

        # Final progress save
        remaining = [u for u in pending_urls if u not in scraped_urls]
        save_progress(scraped_urls, remaining)

        # Export results
        print(f"\n[*] Phase 3: Exporting {len(profiles)} profiles to CSV...")
        export_to_csv(profiles)

        print("\n[+] Done!")

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Saving progress...")
        save_progress(scraped_urls, [u for u in pending_urls if u not in scraped_urls])
        if profiles:
            export_to_csv(profiles, "radiologists_partial.csv")
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        raise
    finally:
        print("[*] Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
