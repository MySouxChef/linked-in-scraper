import re
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def _safe_text(driver, css_selector):
    """Extract text from an element, return empty string if not found."""
    try:
        el = driver.find_element(By.CSS_SELECTOR, css_selector)
        return el.text.strip()
    except NoSuchElementException:
        return ""


def _safe_texts(driver, css_selector):
    """Extract text from multiple elements."""
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        return [el.text.strip() for el in elements if el.text.strip()]
    except Exception:
        return []


def parse_profile(driver, profile_url):
    """Extract structured data from a loaded LinkedIn profile page.

    Call this while the profile page is loaded in the driver.
    """
    data = {
        "name": "",
        "headline": "",
        "location": "",
        "profile_url": profile_url,
        "current_employer": "",
        "current_title": "",
        "past_employers": "",
        "education": "",
        "skills": "",
        "certifications": "",
        "about_snippet": "",
        "open_to_work_badge": False,
        "scraped_at": datetime.now().isoformat(),
    }

    # Name
    data["name"] = _safe_text(driver, "h1.text-heading-xlarge") or _safe_text(driver, "h1")

    # Headline
    data["headline"] = _safe_text(driver, ".text-body-medium.break-words")

    # Location
    data["location"] = _safe_text(driver, ".pv-top-card--list .text-body-small:not(.t-black--light)")
    if not data["location"]:
        data["location"] = _safe_text(driver, "span.text-body-small.inline.t-black--light.break-words")

    # About section
    about = _safe_text(driver, "#about ~ .display-flex .inline-show-more-text, section.pv-about-section .pv-about__summary-text")
    if not about:
        about = _safe_text(driver, "[data-generated-suggestion-target='urn:li:fsd_profileActionDelegate'] .inline-show-more-text")
    data["about_snippet"] = about[:500] if about else ""

    # Experience — current and past
    try:
        experience_items = driver.find_elements(
            By.CSS_SELECTOR,
            "#experience ~ .pvs-list__outer-container .pvs-entity--padded"
        )
        if not experience_items:
            experience_items = driver.find_elements(
                By.CSS_SELECTOR,
                "section[id='experience'] li.artdeco-list__item"
            )

        current_set = False
        past_employers = []
        for item in experience_items:
            try:
                title = item.find_element(
                    By.CSS_SELECTOR,
                    ".t-bold .visually-hidden, .t-bold span[aria-hidden='true']"
                ).text.strip()
            except NoSuchElementException:
                title = ""
            try:
                company = item.find_element(
                    By.CSS_SELECTOR,
                    ".t-normal .visually-hidden, .t-14.t-normal span[aria-hidden='true']"
                ).text.strip()
            except NoSuchElementException:
                company = ""

            # Clean up company — sometimes includes "· Full-time" etc.
            company_clean = company.split("·")[0].strip()

            if not current_set and title:
                data["current_title"] = title
                data["current_employer"] = company_clean
                current_set = True
            elif company_clean:
                past_employers.append(f"{title} @ {company_clean}" if title else company_clean)

        data["past_employers"] = " | ".join(past_employers[:5])
    except Exception:
        pass

    # Education
    try:
        edu_items = driver.find_elements(
            By.CSS_SELECTOR,
            "#education ~ .pvs-list__outer-container .pvs-entity--padded"
        )
        edu_list = []
        for item in edu_items:
            try:
                school = item.find_element(
                    By.CSS_SELECTOR,
                    ".t-bold .visually-hidden, .t-bold span[aria-hidden='true']"
                ).text.strip()
                degree = ""
                try:
                    degree = item.find_element(
                        By.CSS_SELECTOR,
                        ".t-normal .visually-hidden, .t-14.t-normal span[aria-hidden='true']"
                    ).text.strip()
                except NoSuchElementException:
                    pass
                edu_list.append(f"{school} — {degree}" if degree else school)
            except NoSuchElementException:
                pass
        data["education"] = " | ".join(edu_list[:5])
    except Exception:
        pass

    # Skills
    skills = _safe_texts(
        driver,
        "#skills ~ .pvs-list__outer-container .t-bold .visually-hidden, "
        "#skills ~ .pvs-list__outer-container .t-bold span[aria-hidden='true']"
    )
    data["skills"] = " | ".join(skills[:10])

    # Certifications
    certs = _safe_texts(
        driver,
        "#licenses_and_certifications ~ .pvs-list__outer-container .t-bold .visually-hidden, "
        "#licenses_and_certifications ~ .pvs-list__outer-container .t-bold span[aria-hidden='true']"
    )
    data["certifications"] = " | ".join(certs[:10])

    # Open to Work badge detection
    try:
        page_source = driver.page_source.lower()
        if any(marker in page_source for marker in [
            "open_to_work",
            "open to work",
            "#opentowork",
            "hiring-banner",
            "profile-open-to-badge",
        ]):
            data["open_to_work_badge"] = True
    except Exception:
        pass

    # Also check for the OTW photo frame via img alt text
    try:
        photo = driver.find_element(By.CSS_SELECTOR, ".pv-top-card-profile-picture__image, .profile-photo-edit__preview")
        alt = (photo.get_attribute("alt") or "").lower()
        if "open to work" in alt:
            data["open_to_work_badge"] = True
    except Exception:
        pass

    return data
