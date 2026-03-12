# 🎯 ByteForge LeadGen-Sniper V3: Deep Intelligence

> **From Scraper to Business Intelligence.** LeadGen-Sniper V3 is a high-performance lead generation and enrichment suite designed for professional business development and SEO agencies.

---

## 🚀 The V3 Advantage: "High-Intel" Extraction

LeadGen-Sniper V3 moves beyond simple scraping to provide **Deep Business Intelligence**. It doesn't just find names; it audits businesses to find your next payout.

### 💎 Key Features
- **Deep Crawl™ Technology**: Mult-selector engine that resolves issues with Google Maps UI updates and handles headless browser transitions.
- **Website Health Auditor**: Highlighting business value in real-time. Leads missing websites are flagged—your primary targets for web dev services.
- **SEO Intelligence Check**: Built-in website audit detects broken URLs, mobile-unfriendliness, and SEO gaps.
- **C++ Enrichment Engine**: High-speed secondary worker (with Python fallback) for parallel data verification and health checks.
- **Localization Intelligence**: Automatic detection of non-English leads (e.g., Hebrew) with manual review flags for outreach accuracy.
- **Honest Metrics**: Clear reporting when search criteria yield fewer results than requested.
- **Negative Keyword Filter**: Automatic exclusion of false positives like schools and universities.
- **Balanced Sorting**: Intelligent ranking based on rating, review volume, distance, and digital presence.

## 🛠️ Tech Stack
- **Engine**: Python 3.11+, Playwright (Chromium)
- **High-Speed Worker**: C++17 (with Python Enrichment Fallback)
- **UI/UX**: Rich, Click
- **Data**: Pandas, Requests

## 📂 Architecture
- `src/main.py`: The "Brain." Handles CLI, logic, and intelligence orchestration.
- `src/scraper.py`: The "Scout." Deep Crawl orchestration via Playwright.
- `src/parser.py`: The "Analyst." Extracts structured data from listing panels.
- `src/enrichment_worker.py`: The "Specialist." High-speed SEO health auditing.
- `src/enrichment_worker.cpp`: High-performance source code for the enrichment engine.

## 📥 Installation

1. **Clone & Setup**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **(Optional) Compile C++ Engine**:
   ```cmd
   build_worker.bat
   ```
   *Note: If no C++ compiler is found, the tool automatically uses the Python Enrichment Fallback.*

## 🕹️ Usage

Launch the V3 suite with an interactive guide:
```bash
python src/main.py
```

Or skip prompts for automation:
```bash
python src/main.py --niche "mechanic" --location "Tel Aviv" --max-results 20
```

## 📊 Output
All leads are analyzed, scored (Balanced Scoring), and exported to `leads.csv` with 12+ data points, including:
- **Health Score**: 0-100 indicating website quality.
- **Intelligence**: Concrete SEO issues detected.
- **Unverified Flag**: Identifying businesses with 0 reviews (high trust alerts).

## 🛡️ Security & Git
- `.gitignore`: Configured to exclude local caches and private lead data (e.g., `data/*.csv`).
- `data/`: Local directory for exported results (ignored by Git to protect lead privacy).


---
*Developed by ByteForge. Created for the Senior Software Engineering Portfolio.*
