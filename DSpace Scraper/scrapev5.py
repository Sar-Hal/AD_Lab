import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import time
import os
import pandas as pd
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

DELAY = 0.7

SAVE_FOLDER = "downloads"
LOG_FOLDER = "logs"

os.makedirs(SAVE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

CSV_LOG = os.path.join(LOG_FOLDER, "scraped_data.csv")
TXT_LOG = os.path.join(LOG_FOLDER, "scrape_log.txt")

# ================= SESSION =================

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

# ================= LOGGING =================

def log_txt(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)

    with open(TXT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ================= REQUEST =================

def get_page(url):
    try:
        r = session.get(url, timeout=25)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log_txt(f"ERROR fetching {url} : {e}")
        return None

# ================= SEARCH =================

def search_url(term):
    return f"{BASE_URL}/dspace/simple-search?query={term.replace(' ', '+')}"

# ================= PARSERS =================

def extract_item_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/handle/123456789/" in href and "simple-search" not in href:
            links.append(urljoin(BASE_URL, href))

    return list(set(links))

def extract_pdf_links(item_url):
    html = get_page(item_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    pdfs = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "bitstream" in href and ".pdf" in href:
            pdfs.add(urljoin(BASE_URL, href))

    return list(pdfs)

def filename_from_url(pdf_url):
    return unquote(pdf_url.split("/")[-1])

# ================= DOWNLOAD =================

def download_pdf(pdf_url):
    filename = filename_from_url(pdf_url)
    filepath = os.path.join(SAVE_FOLDER, filename)

    if os.path.exists(filepath):
        return "EXISTS"

    try:
        r = session.get(pdf_url, stream=True)
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        return "DOWNLOADED"

    except Exception as e:
        log_txt(f"Download failed {pdf_url} : {e}")
        return "FAILED"

# ================= CSV LOG =================

def append_csv(rows):

    df = pd.DataFrame(rows)

    if not os.path.exists(CSV_LOG):
        df.to_csv(CSV_LOG, index=False)
    else:
        df.to_csv(CSV_LOG, mode="a", header=False, index=False)

# ================= MAIN SEARCH =================

def smart_scrape():

    all_items = set()

    log_txt("===== START SCRAPE =====")

    # Step 1: Search phase
    for term in SEARCH_TERMS:

        url = search_url(term)
        log_txt(f"Searching term: {term}")
        log_txt(f"Search URL: {url}")

        html = get_page(url)
        if not html:
            continue

        items = extract_item_links(html)

        log_txt(f"Items found for {term}: {len(items)}")

        all_items.update(items)

        time.sleep(DELAY)

    log_txt(f"Total unique candidate items: {len(all_items)}")

    # Step 2: Item + PDF extraction
    csv_rows = []

    for item in tqdm(list(all_items), desc="Processing Items"):

        pdfs = extract_pdf_links(item)

        if not pdfs:
            csv_rows.append({
                "item_url": item,
                "pdf_url": "",
                "filename": "",
                "matched": False,
                "download_status": "NO PDF"
            })
            continue

        for pdf in pdfs:

            fname = filename_from_url(pdf)

            match = any(
                term.lower().replace(" ", "") in fname.lower().replace(" ", "")
                for term in SEARCH_TERMS
            )

            status = "SKIPPED"

            if match:
                log_txt(f"MATCH FOUND: {fname}")
                status = download_pdf(pdf)

            csv_rows.append({
                "item_url": item,
                "pdf_url": pdf,
                "filename": fname,
                "matched": match,
                "download_status": status
            })

        time.sleep(DELAY)

    append_csv(csv_rows)

    log_txt("===== SCRAPE COMPLETE =====")

# ================= RUN =================

if __name__ == "__main__":
    smart_scrape()
