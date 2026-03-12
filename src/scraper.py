import asyncio
from playwright.async_api import async_playwright
from rich.progress import Progress
from parser import DataParser
import json
import os

class MapsScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.config = self._load_config()

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {"headless": True, "scroll_attempts": 5, "wait_time": 2}

    async def _scroll_feed(self, page):
        """Scrolls the Google Maps results feed to load more listings."""
        try:
            feed = page.locator('div[role="feed"]')
            if await feed.is_visible():
                await feed.evaluate("el => el.scrollBy(0, 2000)")
                await asyncio.sleep(self.config.get("wait_time", 2))
        except:
            pass

    async def scrape_locations(self, niche, location, max_results):
        """Main scraping loop with Deep Crawl logic."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                locale="en-US"
            )
            page = await context.new_page()
            
            search_query = f"{niche} in {location}"
            print(f"[*] Searching for: {search_query}")
            
            await page.goto("https://www.google.com/maps", wait_until="load")
            
            # Consent handling (More robust)
            try:
                consent_selectors = [
                    'button[aria-label="Accept all"]', 
                    'button:has-text("Accept all")', 
                    'button:has-text("I agree")',
                    'button:has-text("Agree")',
                    'form[action*="consent"] button'
                ]
                for selector in consent_selectors:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=3000):
                        await btn.click()
                        await asyncio.sleep(1)
                        break
            except: pass

            results = []
            seen_names = set()
            
            try:
                # Wait for search box using multiple common selectors
                selectors = [
                    'input[id="searchboxinput"]',
                    'input[aria-label*="Search"]',
                    'input[name="q"]',
                    '#searchboxinput'
                ]
                
                search_box = None
                for selector in selectors:
                    loc = page.locator(selector).first
                    if await loc.is_visible(timeout=5000):
                        search_box = loc
                        break
                
                if not search_box:
                    raise Exception("Could not find search box even after waiting.")

                await search_box.fill(search_query)
                await page.keyboard.press("Enter")
                
                # Wait for feed
                await page.wait_for_selector('div[role="feed"]', timeout=45000)
                
                with Progress() as progress:
                    task = progress.add_task("[cyan]High-Intel Scraping...", total=max_results)
                    
                    while len(results) < max_results:
                        await self._scroll_feed(page)
                        listing_elements = await page.locator('div[role="article"]').all()
                        
                        initial_count = len(results)
                        for el in listing_elements:
                            if len(results) >= max_results: break
                                
                            name = await el.get_attribute("aria-label")
                            if name and name not in seen_names:
                                # DEEP CRAWL: Click listing to see details
                                try:
                                    await el.click()
                                    await asyncio.sleep(1.5) # Wait for panel slide-in
                                    
                                    # Parse from the detailed side panel
                                    # Detailed panel is usually div[role="main"] or has specific aria-label
                                    side_panel = page.locator('div[role="main"]').first
                                    data = await DataParser.parse_listing(side_panel)
                                    
                                    if data:
                                        # Use the name from listing if panel name fails
                                        if data['name'] == "N/A": data['name'] = name
                                        
                                        # Deduplicate
                                        if data['name'] not in seen_names:
                                            results.append(data)
                                            seen_names.add(data['name'])
                                            progress.update(task, advance=1)
                                except Exception as e:
                                    # Fallback if click fails
                                    data = await DataParser.parse_listing(el)
                                    if data:
                                        results.append(data)
                                        seen_names.add(name)
                                        progress.update(task, advance=1)
                        
                        if len(results) == initial_count: break

                await browser.close()
                return results

            except Exception as e:
                print(f"[!] Scrape error: {e}")
                await browser.close()
                return []
