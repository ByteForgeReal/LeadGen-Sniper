"""
scraper.py - Core Google Maps scraper using Playwright (async)
"""

import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeout
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

# Find config.json — works whether flat in src/ or one level up
def _find_config() -> Path:
    here = Path(__file__).parent
    for candidate in [here / "config.json", here.parent / "config.json"]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("config.json not found next to scraper.py or one folder up.")

with open(_find_config()) as f:
    CONFIG = json.load(f)


# ── Coordinate extraction ────────────────────────────────────────────────────

_COORD_RE = re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)")
_CENTER_RE = re.compile(r"center=(-?\d+\.\d+),(-?\d+\.\d+)")


async def get_coords(page: Page):
    """
    Poll the address bar URL for up to 4 seconds waiting for Maps JS to
    inject @lat,lng. Falls back to og:image and canonical tag if it never
    appears in the URL.
    """
    # Poll the address bar — Maps JS writes coords here within 1-3s of load
    for _ in range(8):
        m = _COORD_RE.search(page.url)
        if m:
            return m.group(1), m.group(2)
        await asyncio.sleep(0.5)

    # Fallback A: og:image static-map thumbnail → center=lat,lng
    try:
        og = await page.get_attribute('meta[property="og:image"]', "content") or ""
        m = _CENTER_RE.search(og) or _COORD_RE.search(og)
        if m:
            return m.group(1), m.group(2)
    except Exception:
        pass

    # Fallback B: canonical link tag
    try:
        c = await page.get_attribute('link[rel="canonical"]', "href") or ""
        m = _COORD_RE.search(c)
        if m:
            return m.group(1), m.group(2)
    except Exception:
        pass

    return None, None


async def build_maps_url(page: Page, fallback_url: str) -> str:
    """
    Build a universal Google Maps URL using ?q=lat,lng format.
    Works in every browser, Excel, and mobile without encoding issues.
    Example: https://maps.google.com/?q=30.2003,-97.8003
    """
    lat, lng = await get_coords(page)
    if lat and lng:
        return f"https://maps.google.com/?q={lat},{lng}"
    # Fallback: place name search (no coords available)
    place_match = re.search(r"/maps/place/([^/@?#]+)", page.url or fallback_url)
    place_name  = place_match.group(1) if place_match else "place"
    return f"https://maps.google.com/?q={place_name}"


# ── Scroll ───────────────────────────────────────────────────────────────────

async def scroll_results(page: Page, max_results: int, progress, task) -> list:
    scroll_attempts = 0
    last_count      = 0
    stale_count     = 0

    while scroll_attempts < CONFIG["max_scroll_attempts"]:
        cards         = await page.query_selector_all('a[href*="/maps/place/"]')
        current_count = len(cards)

        progress.update(task, completed=min(current_count, max_results),
                        description=f"[cyan]🗺  Scrolling... {current_count} listings found")

        if current_count >= max_results:
            break
        if await page.query_selector('span.HlvSq'):
            break
        if current_count == last_count:
            stale_count += 1
            if stale_count >= 4:
                break
        else:
            stale_count = 0

        last_count = current_count

        try:
            panel = await page.query_selector('div[role="feed"]')
            if panel:
                await panel.evaluate("el => el.scrollBy(0, 800)")
            else:
                await page.mouse.wheel(0, 800)
        except Exception:
            await page.mouse.wheel(0, 800)

        await asyncio.sleep(CONFIG["scroll_pause"])
        scroll_attempts += 1

    return await page.query_selector_all('a[href*="/maps/place/"]')


# ── Detail extractor ─────────────────────────────────────────────────────────

async def extract_listing_detail(page: Page, url: str) -> dict:
    data = {
        "Business Name":     "",
        "Rating":            "",
        "Number of Reviews": "",
        "Phone Number":      "",
        "Address":           "",
        "Open in Maps":      "",
    }

    try:
        # domcontentloaded — fast, never hangs on Google Maps
        await page.goto(url, wait_until="domcontentloaded", timeout=CONFIG["timeout"])

        # Wait for the h1 business name — signals the info panel is rendered
        try:
            await page.wait_for_selector(
                'h1.DUwDvf, h1[class*="fontHeadlineLarge"]',
                timeout=8000
            )
        except PlaywrightTimeout:
            pass  # panel slow — extract whatever loaded

        # build_maps_url polls until @lat,lng appears in URL (up to 4s)
        data["Open in Maps"] = await build_maps_url(page, url)

        # Business Name
        try:
            el = await page.query_selector('h1.DUwDvf, h1[class*="fontHeadlineLarge"]')
            if el:
                data["Business Name"] = (await el.inner_text()).strip()
        except Exception:
            pass

        # Rating
        try:
            el = await page.query_selector('div.F7nice span[aria-hidden="true"]')
            if el:
                data["Rating"] = (await el.inner_text()).strip()
        except Exception:
            pass

        # Reviews
        try:
            el = await page.query_selector('div.F7nice span[aria-label*="review"]')
            if el:
                label = await el.get_attribute("aria-label")
                m = re.search(r"([\d,]+)", label or "")
                if m:
                    data["Number of Reviews"] = m.group(1).replace(",", "")
        except Exception:
            pass

        # Address & Phone
        try:
            for btn in await page.query_selector_all('button[data-item-id], a[data-item-id]'):
                item_id = await btn.get_attribute("data-item-id") or ""
                aria    = await btn.get_attribute("aria-label") or ""
                text    = (await btn.inner_text()).strip()
                if "address" in item_id.lower() and not data["Address"]:
                    data["Address"] = text or aria.replace("Address: ", "")
                elif "phone" in item_id.lower() and not data["Phone Number"]:
                    data["Phone Number"] = text or aria.replace("Phone: ", "")
        except Exception:
            pass

        # Fallback phone
        if not data["Phone Number"]:
            try:
                body = await page.inner_text("body")
                m = re.search(r"\(?\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4}", body)
                if m:
                    data["Phone Number"] = m.group(0)
            except Exception:
                pass

    except PlaywrightTimeout:
        console.print(f"[red]✗ Hard timeout, skipping: {url[:55]}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {url[:55]} — {e}[/red]")

    return data


# ── Main ─────────────────────────────────────────────────────────────────────

async def run_scraper(niche: str, location: str, max_results: int) -> list[dict]:
    query      = f"{niche} in {location}"
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

    console.print(f"\n[bold cyan]🔍 Searching:[/bold cyan] [white]{query}[/white]")
    console.print(f"[bold cyan]🎯 Max results:[/bold cyan] [white]{max_results}[/white]\n")

    leads = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=CONFIG["headless"])
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            console.print("[dim]Opening Google Maps...[/dim]")
            # domcontentloaded for the search page too — never networkidle on Maps
            await page.goto(search_url, wait_until="domcontentloaded", timeout=CONFIG["timeout"])

            # Wait for the sidebar feed to appear
            try:
                await page.wait_for_selector('div[role="feed"]', timeout=10000)
            except PlaywrightTimeout:
                pass

            await asyncio.sleep(1.5)

            try:
                accept_btn = await page.query_selector('button[aria-label*="Accept"], form button')
                if accept_btn:
                    await accept_btn.click()
                    await asyncio.sleep(0.8)
            except Exception:
                pass

            # Scroll phase
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                          TimeElapsedColumn(), console=console) as progress:
                scroll_task = progress.add_task("[cyan]Scrolling listings...", total=max_results)
                listing_els = await scroll_results(page, max_results, progress, scroll_task)
                progress.update(scroll_task, completed=max_results)

            urls, seen = [], set()
            for el in listing_els:
                href = await el.get_attribute("href")
                if href and href not in seen and "/maps/place/" in href:
                    seen.add(href)
                    urls.append(href)
                    if len(urls) >= max_results:
                        break

            console.print(f"\n[green]Found {len(urls)} listings. Extracting...[/green]\n")

            # Extract phase
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), TextColumn("{task.completed}/{task.total}"),
                          TimeElapsedColumn(), console=console) as progress:
                task = progress.add_task("[cyan]Extracting...", total=len(urls))

                for i, url in enumerate(urls):
                    progress.update(task, description=f"[cyan]Extracting ({i+1}/{len(urls)})...")
                    data = await extract_listing_detail(page, url)
                    if data["Business Name"]:
                        leads.append(data)
                    progress.advance(task)
                    await asyncio.sleep(CONFIG["rate_limit_delay"])

        except Exception as e:
            console.print(f"[bold red]Fatal: {e}[/bold red]")
            raise
        finally:
            await browser.close()

    return leads