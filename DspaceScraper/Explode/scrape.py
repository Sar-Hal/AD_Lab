import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import time
import os
import pandas as pd
import json
from tqdm import tqdm
from datetime import datetime

# ================= CONFIG =================

BASE_URL = "http://10.2.0.84:8080"

SEARCH_TERMS = [
    "HS 30225",
    "HS30225",
    "30225",
    "Leadership",
    "Team Effectiveness",
    "Leadership Team"
]

DELAY = 0.5
SAVE_HTML = True   # GOD MODE SWITCH

SAVE_FOLDER = "downloads"
LOG_FOLDER = "logs"
HTML_FOLDER = os.path.join(LOG_FOLDER, "html_snapshots")

os.makedirs(SAVE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(HTML_FOLDER, exist_ok=True)

CSV_LOG = os.path.join(LOG_FOLDER, "full_scrape.csv")
JSON_LOG = os.path.join(LOG_FOLDER, "full_scrape.json")
EVENT_LOG = os.path.join(LOG_FOLDER, "event_log.txt")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

ALL_DATA = []

# ================= LOGGING =================

def log_event(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)

    with open(EVENT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ================= HELPERS =================

def save_html_snapshot(name, html):
    if not SAVE_HTML:
        return

    safe_name = name.replace("/", "_").replace(":", "_")
    path = os.path.join(HTML_FOLDER, safe_name + ".html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

# ================= REQUEST =================

def get_page(url, label="page"):
    log_event(f"REQUEST → {url}")

    try:
        r = session.get(url, timeout=25)
        r.raise_for_status()

        if SAVE_HTML:
            save_html_snapshot(label + "_" + str(time.time()), r.text)

        return r.text

    except Exception as e:
        log_event(f"ERROR REQUEST {url} : {e}")
        return None

# ================= PARSERS =================

def extract_item_links(html, source="unknown"):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/handle/123456789/" in href and "simple-search" not in href:
            full = urljoin(BASE_URL, href)
            links.append(full)

    log_event(f"EXTRACT ITEM LINKS → Found {len(links)} from {source}")

    return list(set(links))

def extract_pdf_links(item_url):
    html = get_page(item_url, "item_page")

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    pdfs = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "bitstream" in href and ".pdf" in href:
            full = urljoin(BASE_URL, href)
            pdfs.append(full)

    log_event(f"PDF LINKS → {len(pdfs)} found in {item_url}")

    return list(set(pdfs))

def filename_from_url(pdf_url):
    return unquote(pdf_url.split("/")[-1])

# ================= DOWNLOAD =================

def download_pdf(pdf_url):
    fname = filename_from_url(pdf_url)
    path = os.path.join(SAVE_FOLDER, fname)

    if os.path.exists(path):
        log_event(f"DOWNLOAD SKIP (exists) → {fname}")
        return "EXISTS"

    try:
        r = session.get(pdf_url, stream=True)

        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        log_event(f"DOWNLOAD SUCCESS → {fname}")
        return "DOWNLOADED"

    except Exception as e:
        log_event(f"DOWNLOAD FAILED → {pdf_url} : {e}")
        return "FAILED"

# ================= MAIN =================

def search_url(term):
    return f"{BASE_URL}/dspace/simple-search?query={term.replace(' ', '+')}"

def run_full_scrape():

    global ALL_DATA

    start = time.time()

    all_items = set()

    # SEARCH PHASE
    for term in SEARCH_TERMS:

        url = search_url(term)

        log_event(f"SEARCH TERM → {term}")

        html = get_page(url, "search_page")

        if not html:
            continue

        items = extract_item_links(html, term)

        all_items.update(items)

        time.sleep(DELAY)

    log_event(f"TOTAL UNIQUE ITEMS → {len(all_items)}")

    # ITEM PHASE
    for item in tqdm(list(all_items), desc="ITEM PROCESS"):

        pdfs = extract_pdf_links(item)

        if not pdfs:
            ALL_DATA.append({
                "item_url": item,
                "pdf_url": "",
                "filename": "",
                "matched": False,
                "download": "NO PDF"
            })
            continue

        for pdf in pdfs:

            fname = filename_from_url(pdf)

            match = any(
                t.lower().replace(" ", "") in fname.lower().replace(" ", "")
                for t in SEARCH_TERMS
            )

            log_event(f"CHECK FILE → {fname} | MATCH = {match}")

            status = "SKIPPED"

            if match:
                status = download_pdf(pdf)

            ALL_DATA.append({
                "item_url": item,
                "pdf_url": pdf,
                "filename": fname,
                "matched": match,
                "download": status
            })

        time.sleep(DELAY)

    # SAVE DATASET
    pd.DataFrame(ALL_DATA).to_csv(CSV_LOG, index=False)

    with open(JSON_LOG, "w") as f:
        json.dump(ALL_DATA, f, indent=2)

    log_event(f"TOTAL TIME → {(time.time()-start)/60:.2f} min")

# ================= RUN =================

if __name__ == "__main__":
    run_full_scrape()
