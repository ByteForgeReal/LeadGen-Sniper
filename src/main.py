"""
main.py - LeadGen Sniper entry point
Interactive prompt-based interface (no CLI flags needed)
"""

import asyncio
import sys
import os

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.columns import Columns
from rich import box

from scraper import run_scraper
from exporter import export_leads, print_preview

console = Console()

YOUTUBE_URL = "https://www.youtube.com/channel/UCC05rPMVdEhh6FCG126M6jg"


def print_banner():
    banner = Text()
    banner.append("🎯  LeadGen Sniper\n", style="bold cyan")
    banner.append("Scrape Google Maps → Export clean lead lists", style="dim white")
    console.print(Panel(banner, box=box.DOUBLE_EDGE, border_style="cyan", padding=(1, 4)))
    console.print()


def print_signature():
    sig = Text()
    sig.append("\n  ⚒  ", style="bold yellow")
    sig.append("ByteForge", style="bold white")
    sig.append("  —  ", style="dim white")
    sig.append("YouTube", style="bold red")
    sig.append(f"  {YOUTUBE_URL}\n", style="dim cyan underline")
    console.print(Panel(sig, box=box.SIMPLE, border_style="dim yellow", padding=(0, 2)))


def get_user_inputs() -> tuple[str, str, int]:
    """Interactive prompts — no CLI flags needed."""
    console.print("[bold white]Let's set up your search:[/bold white]\n")

    niche = Prompt.ask(
        "[bold yellow]🔧 Business niche[/bold yellow]",
        default="mechanic"
    ).strip()

    location = Prompt.ask(
        "[bold yellow]📍 Location[/bold yellow]",
        default="Austin Texas"
    ).strip()

    max_results = IntPrompt.ask(
        "[bold yellow]📊 Max results[/bold yellow]",
        default=20
    )
    max_results = max(1, min(max_results, 200))

    console.print()
    return niche, location, max_results


def confirm_search(niche: str, location: str, max_results: int) -> bool:
    console.print(Panel(
        f"[bold]Niche:[/bold]    [cyan]{niche}[/cyan]\n"
        f"[bold]Location:[/bold] [cyan]{location}[/cyan]\n"
        f"[bold]Results:[/bold]  [cyan]{max_results}[/cyan]",
        title="[bold green]✅ Search Summary[/bold green]",
        border_style="green",
        padding=(0, 2)
    ))
    confirm = Prompt.ask("\n[bold]Proceed?[/bold] [dim](y/n)[/dim]", default="y")
    return confirm.lower().strip() in ("y", "yes", "")


async def main():
    print_banner()

    try:
        niche, location, max_results = get_user_inputs()

        if not confirm_search(niche, location, max_results):
            console.print("[yellow]Search cancelled.[/yellow]")
            print_signature()
            return

        console.print()
        leads = await run_scraper(niche, location, max_results)

        if not leads:
            console.print("[bold red]No leads were collected. Try a different niche or location.[/bold red]")
            print_signature()
            return

        # Preview
        print_preview(leads, n=5)

        # Export
        export_leads(leads, output_path="leads.csv")

        console.print(f"\n[bold green]🎉 Done! {len(leads)} leads saved to leads.csv[/bold green]")

        # Ask if user wants to run again
        again = Prompt.ask("\n[bold]Run another search?[/bold] [dim](y/n)[/dim]", default="n")
        if again.lower().strip() in ("y", "yes"):
            await main()
        else:
            print_signature()

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        print_signature()
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())