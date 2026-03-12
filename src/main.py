import click
import asyncio
import json
import os
import math
import sys
import requests
import subprocess
from scraper import MapsScraper
from exporter import Exporter
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Force UTF-8 encoding for Hebrew support on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

console = Console()

NEG_KEYWORDS = ["school", "academy", "university", "college", "institute", "bootcamp"]

def detect_location():
    """Detects the current location of the user based on IP address."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def filter_negative_leads(leads):
    """Filters out leads containing negative keywords (False Positives)."""
    filtered = []
    removed_count = 0
    for lead in leads:
        name_lower = lead['name'].lower()
        if any(kw in name_lower for kw in NEG_KEYWORDS):
            removed_count += 1
            continue
        filtered.append(lead)
    return filtered, removed_count

def run_enrichment_worker(leads):
    """
    Calls the C++ Enrichment Worker to perform fast website health checks.
    """
    if not leads: return leads
    
    # Save current leads to temp file for C++ worker
    temp_in = "temp_leads_in.json"
    temp_out = "temp_leads_out.json"
    
    with open(temp_in, "w") as f:
        json.dump(leads, f)
    
    # Check if worker is compiled
    worker_exe = "./enrichment_worker.exe" if sys.platform == "win32" else "./enrichment_worker"
    worker_py = os.path.join(os.path.dirname(__file__), "enrichment_worker.py")
    
    try:
        if os.path.exists(worker_exe):
            console.print("[*] Running [bold green]C++ Enrichment Worker[/bold green] for high-speed SEO check...")
            subprocess.run([worker_exe, temp_in, temp_out], check=True)
        elif os.path.exists(worker_py):
            console.print("[*] Running [bold blue]Python Enrichment Fallback[/bold blue] (Source Only)...")
            subprocess.run([sys.executable, worker_py, temp_in, temp_out], check=True)
        else:
            console.print("[dim][!] Enrichment worker not found. Skipping SEO check.[/dim]")
            return leads

        if os.path.exists(temp_out):
            with open(temp_out, "r") as f:
                return json.load(f)
    except Exception as e:
        console.print(f"[yellow][!] Enrichment failed: {e}.[/yellow]")
    
    return leads

def generate_pitch(lead):
    """Generates a cold email pitch based on the lead's enriched data."""
    name = lead['name']
    has_website = lead['website'] != "None"
    seo_issue = lead.get('seo_issue', "")
    
    if not has_website:
        return f"""
Subject: Help with your online presence - {name}

Hi there, I noticed {name} doesn't have a website yet. In today's market, you're losing customers to competitors who do. I build professional sites that win clients. Can we chat?
"""
    elif seo_issue:
        return f"""
Subject: Fixing {name}'s Website Issues

Hi there, I noticed your website has some tech issues ({seo_issue}). This hurts your Google ranking. I'm a dev who specializes in fixing these exact problems. Open to a 5-min talk?
"""
    return f"Subject: Scaling {name}'s growth\nHi, I love your brand! I'd love to help you scale your digital presence. Can we talk?"

def display_leads(leads, sort_by="balanced"):
    """Displays leads in a beautiful table with high-intel indicators."""
    if not leads: return []

    # Sort logic
    if sort_by == "rating":
        sorted_leads = sorted(leads, key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_by == "distance":
        sorted_leads = sorted(leads, key=lambda x: x.get('distance_km', 999.0))
    else: # balanced
        # Simple balanced score: Rating * log(Reviews+1) - (Distance Penalty)
        sorted_leads = sorted(leads, key=lambda x: (x.get('rating', 0) * math.log10(x.get('reviews', 0)+1)) - (min(x.get('distance_km', 999)/2, 5)), reverse=True)

    table = Table(title=f"ByteForge Intelligence: [bold green]{len(leads)} High-Value Leads[/bold green]", box=None)
    table.add_column("Business Name", style="cyan", width=35)
    table.add_column("Rating", justify="center")
    table.add_column("Website Audit", justify="center")
    table.add_column("Phone", style="white")
    table.add_column("Intelligence", style="dim")

    for lead in sorted_leads[:20]:
        # Website status + Performance Health
        site = lead.get('website', "None")
        health = lead.get('health_score', 100)
        
        if site == "None":
            site_display = "[bold red]MISSING[/bold red]"
        elif health < 70:
            site_display = f"[bold yellow]BROKEN ({health}%)[/bold yellow]"
        else:
            site_display = "[bold green]HEALTHY[/bold green]"
            
        rating = f"[yellow]{lead['rating']}[/yellow] ([dim]{lead['reviews']}[/dim])" if lead['reviews'] > 0 else "[dim]Unverified[/dim]"
        intel = lead.get('seo_issue', "Ready for outreach")
        
        table.add_row(
            lead['name'],
            rating,
            site_display,
            lead['phone'],
            intel
        )

    console.print(table)
    return sorted_leads

@click.command()
@click.option("--niche", prompt="Business Niche", help="e.g., 'mechanic'")
@click.option("--location", prompt="City/Region", help="e.g., 'Tokyo'")
@click.option("--max-results", default=10, prompt="Lead Count", help="Max leads to scrape")
def main(niche, location, max_results):
    console.print(f"\n[bold magenta]ByteForge LeadGen-Sniper V3: Deep Intelligence[/bold magenta]")
    
    # Start location for haversine (future use)
    start_info = detect_location()
    
    scraper = MapsScraper(headless=True)
    leads = asyncio.run(scraper.scrape_locations(niche, location, max_results))
    
    if leads:
        # 1. Negative Keyword Filtering
        leads, removed = filter_negative_leads(leads)
        if removed > 0:
            console.print(f"[*] Intelligence Filter: Removed [bold red]{removed}[/bold red] false positives (Schools/Academies).")

        # 2. Quality Filter (Reviews)
        if Confirm.ask("\nFilter unverified leads (0 reviews)?"):
            leads = [l for l in leads if l['reviews'] > 0]
            console.print(f"[*] Quality Filtered: [bold green]{len(leads)} remaining[/bold green]")

        # 3. C++ Enrichment & SEO Health Check
        leads = run_enrichment_worker(leads)
        
        # 4. Sorting & Display
        choice = Prompt.ask("\nSort by", choices=["balanced", "rating", "distance"], default="balanced")
        sorted_leads = display_leads(leads, sort_by=choice)
        
        # 5. Pitch Generator
        if sorted_leads and Confirm.ask("\nGenerate Intelligence Report + Pitch for the #1 lead?"):
            pitch = generate_pitch(sorted_leads[0])
            console.print("\n[bold cyan]--- AI GENERATED OUTREACH ---[/bold cyan]")
            console.print(pitch)
            console.print("[bold cyan]-----------------------------[/bold cyan]\n")

        if Confirm.ask("Export to data/leads.csv?", default=True):
            Exporter.to_csv(sorted_leads, "data/leads.csv")
            console.print("[bold green][√] Export complete.[/bold green]")
    else:
        console.print("[red]No leads found.[/red]")

if __name__ == "__main__":
    main()
