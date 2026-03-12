import re
from playwright.async_api import Locator

class DataParser:
    @staticmethod
    async def parse_listing(element: Locator):
        """
        Extracts high-fidelity data from a detailed Google Maps listing panel.
        """
        try:
            # Full text content of the panel
            text_content = await element.inner_text()
            lines = text_content.split('\n')
            
            # Name extraction from the panel header
            name = "N/A"
            try:
                # Panel headers often use h1 or specific font size
                header = element.locator('h1').first
                if await header.is_visible(timeout=500):
                    extracted_name = await header.inner_text()
                    # Skip common "Results" headers in different languages
                    if extracted_name.strip() in ["Results", "תוצאות", "Showing results"]:
                        return None
                    name = extracted_name
            except:
                pass

            # Rating and Reviews
            rating = 0.0
            reviews = 0
            # Common pattern: "4.5 stars (120 reviews)"
            rating_match = re.search(r"([\d\.]+)\s?stars?\s?\(?([\d,]+)\)?", text_content, re.IGNORECASE)
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                    reviews_str = rating_match.group(2).replace(',', '')
                    reviews = int(reviews_str)
                except: pass

            # Detailed Distance if available
            distance = "N/A"
            distance_km = 999.0
            dist_match = re.search(r"([\d\.]+)\s?(km|m|miles|mi)\b", text_content, re.IGNORECASE)
            if dist_match:
                distance = dist_match.group(0)
                try:
                    val = float(dist_match.group(1))
                    unit = dist_match.group(2).lower()
                    if unit == 'm': distance_km = val / 1000
                    elif 'mile' in unit or unit == 'mi': distance_km = val * 1.609
                    else: distance_km = val
                except: pass

            # Phone - Deep extraction from panel
            phone = "N/A"
            # Look for phone icon/label or specific format
            phone_pattern = r"(\+?\d{1,3}[\s.-]?)?\(?\d{2,3}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}"
            phone_match = re.search(phone_pattern, text_content)
            if phone_match:
                phone = phone_match.group(0)

            # Website - Detailed extraction
            website = "None"
            try:
                # Websites are often in links with aria-label containing "Website"
                web_loc = element.locator('a[aria-label*="Website"]').first
                if await web_loc.is_visible(timeout=500):
                    website = await web_loc.get_attribute("href") or "None"
                # Alternative: look for icons or specific data-value
                elif await element.locator('a[data-value="Website"]').is_visible(timeout=200):
                    website = await element.locator('a[data-value="Website"]').get_attribute("href") or "None"
            except: pass

            # Address
            address = "N/A"
            # Address usually has a pin icon or specific format
            for line in lines:
                if any(char.isdigit() for char in line) and (',' in line or 'St' in line or 'Rd' in line):
                    if len(line.split(',')) > 1:
                        address = line
                        break

            return {
                "name": name,
                "rating": rating,
                "reviews": reviews,
                "distance": distance,
                "distance_km": distance_km,
                "phone": phone,
                "address": address,
                "website": website,
                "maps_url": f"https://www.google.com/maps/search/{name.replace(' ', '+')}",
                "unverified": reviews == 0
            }
        except Exception as e:
            # print(f"Parser error: {e}")
            return None
