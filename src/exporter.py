"""
exporter.py - Exports lead data to CSV using pandas
Includes string sanitizer (strips non-ASCII) and URL cleaner.
"""

import unicodedata
import pandas as pd
from pathlib import Path
from rich.console import Console

console = Console()

COLUMNS = [
    "Business Name",
    "Rating",
    "Number of Reviews",
    "Phone Number",
    "Address",
    "Open in Maps",
]

# URL markers where data-blob junk begins — split and keep left side only
_URL_JUNK_MARKERS = ["/data=", "!4m", "!1m", "?hl="]


# ── Sanitizers ───────────────────────────────────────────────────────────────

def _strip_non_ascii(value: str) -> str:
    """
    Remove any character outside plain printable ASCII (32–126).
    Catches Hebrew, Arabic, CJK, emoji, and anything else that looks
    broken when a client opens the CSV in Excel.
    """
    if not isinstance(value, str):
        return value
    value = unicodedata.normalize("NFC", value)
    return value.encode("ascii", errors="ignore").decode("ascii").strip()


def _clean_url(url: str) -> str:
    """
    Trim a Google Maps URL to its human-readable base permalink.

    Before: https://www.google.com/maps/place/Joe%27s+Auto/data=!4m7!3m6...
    After:  https://www.google.com/maps/place/Joe's+Auto
    """
    if not isinstance(url, str) or not url:
        return url
    for marker in _URL_JUNK_MARKERS:
        if marker in url:
            url = url.split(marker)[0]
    return url.rstrip("/")


def _sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Strip non-ASCII from text columns and clean the Maps URL."""
    for col in ["Business Name", "Phone Number", "Address"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda v: _strip_non_ascii(v) if pd.notna(v) else v
            )
    if "Open in Maps" in df.columns:
        df["Open in Maps"] = df["Open in Maps"].apply(
            lambda v: _clean_url(v) if pd.notna(v) else v
        )
    return df


# ── Export ───────────────────────────────────────────────────────────────────

def export_leads(leads: list[dict], output_path: str = "leads.csv") -> str:
    """Export lead dicts to CSV. Returns absolute path of saved file."""
    if not leads:
        console.print("[yellow]⚠ No leads to export.[/yellow]")
        return ""

    df = pd.DataFrame(leads, columns=COLUMNS)

    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Number of Reviews"] = pd.to_numeric(df["Number of Reviews"], errors="coerce")

    df.dropna(how="all", inplace=True)
    df.drop_duplicates(subset=["Business Name", "Address"], inplace=True)

    df = _sanitize_dataframe(df)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)

    abs_path = str(output.resolve())
    console.print(f"\n[bold green]✅ Exported {len(df)} leads → {abs_path}[/bold green]")
    return abs_path


# ── Preview ──────────────────────────────────────────────────────────────────

def print_preview(leads: list[dict], n: int = 5):
    """Print a rich table preview of the first N leads."""
    from rich.table import Table

    preview = []
    for lead in leads[:n]:
        clean = {}
        for col in COLUMNS:
            val = lead.get(col, "")
            if isinstance(val, str):
                val = _strip_non_ascii(val)
                if col == "Open in Maps":
                    val = _clean_url(val)
            clean[col] = val
        preview.append(clean)

    table = Table(title=f"📋 Lead Preview (first {min(n, len(leads))})", show_lines=True)
    for col in COLUMNS:
        table.add_column(col, overflow="fold", max_width=30)
    for lead in preview:
        table.add_row(*[str(lead.get(col, "")) for col in COLUMNS])

    console.print(table)