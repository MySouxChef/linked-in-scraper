import pickle
import time
import random
import os

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import (
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
    ACTION_DELAY,
    COOKIE_FILE,
)


def create_browser(headless=True):
    """Create an undetected Chrome browser instance."""
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")

    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def save_cookies(driver):
    """Save browser cookies to disk for session reuse."""
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("[+] Cookies saved.")


def load_cookies(driver):
    """Load cookies from disk if available. Returns True if loaded."""
    if not os.path.exists(COOKIE_FILE):
        return False
    try:
        with open(COOKIE_FILE, "rb") as f:
            cookies = pickle.load(f)
        driver.get("https://www.linkedin.com")
        for cookie in cookies:
            # Selenium requires domain to match
            if "linkedin.com" in cookie.get("domain", ""):
                try:
                    driver.add_cookie(cookie)
                except Exception:
                    pass
        driver.refresh()
        time.sleep(random.uniform(*ACTION_DELAY))
        return _is_logged_in(driver)
    except Exception as e:
        print(f"[!] Failed to load cookies: {e}")
        return False


def _is_logged_in(driver):
    """Check if current session is logged in."""
    try:
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(random.uniform(*ACTION_DELAY))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module, .global-nav__me"))
        )
        return True
    except TimeoutException:
        return False


def login(driver):
    """Log in to LinkedIn. Tries cookies first, falls back to credentials."""
    print("[*] Attempting login...")

    if load_cookies(driver):
        print("[+] Logged in via saved cookies.")
        return True

    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        print("[!] No credentials found. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
        return False

    print("[*] Logging in with credentials...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(random.uniform(*ACTION_DELAY))

    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")

        # Type credentials with human-like delays
        for char in LINKEDIN_EMAIL:
            email_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(random.uniform(0.5, 1.0))

        for char in LINKEDIN_PASSWORD:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(random.uniform(0.5, 1.0))

        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        time.sleep(random.uniform(*ACTION_DELAY))

        # Check for security challenge / CAPTCHA
        if "checkpoint" in driver.current_url or "challenge" in driver.current_url:
            print("[!] Security challenge detected (CAPTCHA or verification).")
            print("[!] Please complete the challenge manually in a non-headless run,")
            print("[!] or try again later with a different IP.")
            return False

        # Verify login succeeded
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module, .global-nav__me"))
        )
        print("[+] Login successful.")
        save_cookies(driver)
        return True

    except TimeoutException:
        print("[!] Login failed — timed out waiting for feed to load.")
        print(f"[!] Current URL: {driver.current_url}")
        return False
    except Exception as e:
        print(f"[!] Login error: {e}")
        return False
