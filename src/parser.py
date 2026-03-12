"""
parser.py - Extracts structured business data from Google Maps listing elements
"""

import re
from typing import Optional


def parse_business_card(card_text: str, url: str = "") -> dict:
    """
    Parse raw text from a Google Maps business card into structured data.
    Returns a dict with all lead fields.
    """
    lines = [line.strip() for line in card_text.strip().splitlines() if line.strip()]

    result = {
        "Business Name": "",
        "Rating": "",
        "Number of Reviews": "",
        "Phone Number": "",
        "Address": "",
        "Website": "",
        "Google Maps URL": url,
    }

    if not lines:
        return result

    # First non-empty line is usually the business name
    result["Business Name"] = lines[0]

    for line in lines[1:]:
        # Rating: looks like "4.5" or "4.5 stars"
        rating_match = re.match(r"^(\d\.\d)\s*(stars?)?$", line, re.IGNORECASE)
        if rating_match and not result["Rating"]:
            result["Rating"] = rating_match.group(1)
            continue

        # Reviews: looks like "(123)" or "123 reviews"
        reviews_match = re.match(r"^\(?([\d,]+)\)?\s*(reviews?)?$", line, re.IGNORECASE)
        if reviews_match and not result["Number of Reviews"]:
            result["Number of Reviews"] = reviews_match.group(1).replace(",", "")
            continue

        # Phone number
        phone_match = re.match(r"^[\+\d\s\(\)\-\.]{7,20}$", line)
        if phone_match and not result["Phone Number"]:
            result["Phone Number"] = line
            continue

        # Website
        if re.match(r"^(www\.|http)", line, re.IGNORECASE) and not result["Website"]:
            result["Website"] = line
            continue

        # Address: heuristic — contains digits and common address words
        address_keywords = ["st", "ave", "blvd", "rd", "dr", "ln", "way", "tx", "ca", "ny", "fl"]
        line_lower = line.lower()
        if (
            not result["Address"]
            and any(kw in line_lower for kw in address_keywords)
            and re.search(r"\d", line)
        ):
            result["Address"] = line
            continue

    return result


def clean_reviews(value: str) -> Optional[int]:
    """Convert review string to integer."""
    try:
        return int(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def clean_rating(value: str) -> Optional[float]:
    """Convert rating string to float."""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None