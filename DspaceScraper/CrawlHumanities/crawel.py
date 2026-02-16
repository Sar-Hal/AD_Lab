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

# BEST TARGET COLLECTIONS
TARGET_HANDLES = [
    95,   # Management Question Bank (Top Priority)
    67,   # Rural Management QB
    131,
    132,
    133,
    134,
    135
]

MATCH_TERMS = [
    "HS 30225",
    "30225",
    "Leadership",
    "Team Effectiveness",
    "Leadership Team"
]

DELAY = 0.5

SAVE_FOLDER = "downloads_multi"
LOG_FOLDER = "logs_multi"

os.makedirs(SAVE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

CSV_LOG = os.path.join(LOG_FOLDER, "multi_full.csv")
EVENT_LOG = os.path.join(LOG_FOLDER, "multi_event.txt")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

ALL_ROWS = []
VISITED_ITEMS = set()

# ================= LOG =================

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)

    with open(EVENT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ================= REQUEST =================

def get_page(url):
    try:
        r = session.get(url, timeout=25)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log(f"ERROR REQUEST {url} : {e}")
        return None

# ================= PARSERS =================

def extract_item_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/handle/123456789/" in href and "simple-search" not in href:
            links.append(urljoin(BASE_URL, href))

    return list(set(links))

def get_next_page(html):
    soup = BeautifulSoup(html, "html.parser")

    next_btn = soup.find("a", string=lambda s: s and "next" in s.lower())

    if next_btn and next_btn.get("href"):
        return urljoin(BASE_URL, next_btn["href"])

    return None

def extract_pdf_links(item_url):
    html = get_page(item_url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    pdfs = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "bitstream" in href and ".pdf" in href:
            pdfs.append(urljoin(BASE_URL, href))

    return list(set(pdfs))

def filename_from_url(pdf_url):
    return unquote(pdf_url.split("/")[-1])

# ================= DOWNLOAD =================

def download_pdf(pdf_url):
    fname = filename_from_url(pdf_url)
    path = os.path.join(SAVE_FOLDER, fname)

    if os.path.exists(path):
        return "EXISTS"

    try:
        r = session.get(pdf_url, stream=True)

        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        return "DOWNLOADED"

    except:
        return "FAILED"

# ================= COLLECTION CRAWL =================

def crawl_collection(handle):

    start_url = f"{BASE_URL}/dspace/handle/123456789/{handle}"

    log(f"\n===== START COLLECTION {handle} =====")

    current = start_url
    page_no = 0

    while current:

        page_no += 1
        log(f"COL {handle} PAGE {page_no} → {current}")

        html = get_page(current)
        if not html:
            break

        items = extract_item_links(html)

        for item in tqdm(items, desc=f"H{handle}-P{page_no}"):

            if item in VISITED_ITEMS:
                continue

            VISITED_ITEMS.add(item)

            pdfs = extract_pdf_links(item)

            if not pdfs:
                ALL_ROWS.append({
                    "collection": handle,
                    "item": item,
                    "pdf": "",
                    "filename": "",
                    "match": False,
                    "download": "NO PDF"
                })
                continue

            for pdf in pdfs:

                fname = filename_from_url(pdf)

                match = any(
                    t.lower().replace(" ", "") in fname.lower().replace(" ", "")
                    for t in MATCH_TERMS
                )

                status = "SKIPPED"

                if match:
                    log(f"MATCH [{handle}] → {fname}")
                    status = download_pdf(pdf)

                ALL_ROWS.append({
                    "collection": handle,
                    "item": item,
                    "pdf": pdf,
                    "filename": fname,
                    "match": match,
                    "download": status
                })

            time.sleep(DELAY)

        current = get_next_page(html)

        if current:
            time.sleep(DELAY)

# ================= MASTER =================

def run_multi():

    start = time.time()

    for h in TARGET_HANDLES:
        crawl_collection(h)

    pd.DataFrame(ALL_ROWS).to_csv(CSV_LOG, index=False)

    log(f"\nTOTAL TIME → {(time.time()-start)/60:.2f} min")

# ================= RUN =================

if __name__ == "__main__":
    run_multi()
