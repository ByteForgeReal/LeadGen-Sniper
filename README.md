<div align="center">

  <a href="https://www.youtube.com/channel/UCC05rPMVdEhh6FCG126M6jg">
    <img src="ByteForge.png" alt="ByteForge" width="200"/>
  </a>

  <h1>⚒️ ByteForge — LeadGen Sniper</h1>

  <p><b>Automated Google Maps Lead Extraction & Export Engine</b><br/>
  <sub>Built for agencies, freelancers, and growth-hackers who close deals with data.</sub></p>

  <a href="https://www.youtube.com/channel/UCC05rPMVdEhh6FCG126M6jg">
    <img src="https://img.shields.io/badge/YouTube-ByteForge-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/>
  </a>
  <a href="https://github.com/ByteForgeReal/LeadGen-Sniper/releases">
    <img src="https://img.shields.io/badge/Download-.EXE-brightgreen?style=for-the-badge&logo=windows&logoColor=white" alt="Download EXE"/>
  </a><br/><br/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?style=for-the-badge&logo=playwright&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-Data%20Engine-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Rich-Terminal%20UI-ff69b4?style=for-the-badge"/>

</div>


---

## 🎯 Overview

LeadGen Sniper turns Google Maps into a structured lead database in minutes. It automates the entire lifecycle — **Search → Scrape → Sanitize → Export** — and hands you a clean `.csv` ready to drop into any CRM or outreach tool.

Perfect for identifying high-value acquisition targets for web development, SEO services, and B2B sales.

```text
🔧 Business niche: mechanic
📍 Location: Austin Texas  
📊 Max results: 50

Opening Google Maps...
Scrolling listings... ████████████ 100%
Extracting (50/50)... ████████████ 100%

✅ 48 leads exported → leads.csv
🎉 Done!
```

---

## 💎 Key Features

| | Feature | Details |
|---|---|---|
| 🗺 | **Smart Coordinate Extraction** | Polls the Maps JS runtime until `lat,lng` appears — never misses a pin |
| 🔗 | **Universal Map Links** | `maps.google.com/?q=lat,lng` — works in Excel, browser, and mobile |
| 🧹 | **Data Sanitizer** | Strips non-ASCII characters (Hebrew, Arabic, CJK) before export |
| 📊 | **Rich Terminal UI** | Live progress bars, lead preview table, coloured status messages |
| ⚡ | **Rate Limiter** | Configurable delay between requests to avoid detection |
| 🛡️ | **Fault Tolerant** | Per-listing timeout catch — one slow page never kills the run |
| 🔁 | **Multi-Search Sessions** | Chain unlimited searches back-to-back in one session |
| ⚙️ | **Config-Driven** | Tune every parameter in `config.json` without touching code |

---

## 📁 Project Structure

```text
LeadGen-Sniper/
│
├── src/
│   ├── main.py          # Entry point — interactive prompts & orchestration
│   ├── scraper.py       # Playwright engine — scroll, navigate, extract
│   ├── exporter.py      # Pandas CSV export + data sanitizer
│   └── parser.py        # Business card text parser utilities
│
├── ByteForge.png        # Project logo
├── config.json          # All tuneable parameters
├── requirements.txt     # Python dependencies
└── README.md
```

---

## 📥 Installation

**1. Clone the repository**
```bash
git clone https://github.com/ByteForgeReal/LeadGen-Sniper.git
cd LeadGen-Sniper
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**3. Install the Playwright browser**
```bash
playwright install chromium
```

---

## ▶️ Usage

```bash
python src/main.py
```

No flags. No config editing needed. Answer three prompts and go:

```text
🔧 Business niche (mechanic): plumber
📍 Location (Austin Texas): New York City
📊 Max results (20): 100

Proceed? (y/n): y
```

Results are saved to `leads.csv` in the project root.

---

## 📊 Output Format

| Column | Example |
|---|---|
| Business Name | Joe's Plumbing |
| Rating | 4.7 |
| Number of Reviews | 312 |
| Phone Number | +1 212-555-0198 |
| Address | 145 W 45th St, New York, NY 10036 |
| Open in Maps | https://maps.google.com/?q=40.7580,-73.9855 |

> The **Open in Maps** column uses `?q=lat,lng` format — click it from Excel, a browser, or your phone and it drops a pin on the exact location with zero encoding errors.

---

## ⚙️ Configuration

```json
{
  "rate_limit_delay": 0.8,
  "scroll_pause": 1.2,
  "max_scroll_attempts": 30,
  "headless": false,
  "timeout": 30000,
  "output_file": "leads.csv"
}
```

| Key | Default | Description |
|---|---|---|
| `rate_limit_delay` | `0.8` | Seconds between each listing request |
| `scroll_pause` | `1.2` | Seconds between scroll steps in the sidebar |
| `max_scroll_attempts` | `30` | Max scroll iterations before stopping |
| `headless` | `false` | `true` = silent background, `false` = watch the browser |
| `timeout` | `30000` | Page load timeout in milliseconds |
| `output_file` | `leads.csv` | Output filename |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Browser Automation | Playwright (Chromium) |
| Data Processing | Pandas |
| Terminal UI | Rich |
| Language | Python 3.11+ |
| Async Runtime | asyncio |

---

## ⚠️ Notes

- Google Maps is a live product — selectors may change over time. If extraction breaks, open an issue.
- Use responsibly. This tool is intended for legitimate business prospecting and research.
- Lowering `rate_limit_delay` below `0.5` may trigger bot detection.
- Tested on Python 3.11, 3.12, and 3.14 on Windows 11.

---

<div align="center">

  <a href="https://www.youtube.com/channel/UCC05rPMVdEhh6FCG126M6jg">
    <img src="https://img.shields.io/badge/▶%20Watch%20on%20YouTube-ByteForge-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/>
  </a>

  <br/><br/>
  <sub>Built with 🔥 by <a href="https://www.youtube.com/channel/UCC05rPMVdEhh6FCG126M6jg"><b>ByteForge</b></a></sub>

</div>
