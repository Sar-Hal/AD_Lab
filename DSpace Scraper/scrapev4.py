import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import time
import os
from tqdm import tqdm

BASE_URL = "http://10.2.0.84:8080"
START_URL = "http://10.2.0.84:8080/dspace/handle/123456789/32"

TARGET_COURSE = "HS 30225"

SAVE_FOLDER = "downloads"
DELAY = 1.5

os.makedirs(SAVE_FOLDER, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def get_page(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    except:
        return None


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

    pdfs = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "bitstream" in href and ".pdf" in href:
            pdfs.add(urljoin(BASE_URL, href))

    return list(pdfs)


def filename_from_url(pdf_url):
    return unquote(pdf_url.split("/")[-1])


def download_pdf(pdf_url):
    filename = filename_from_url(pdf_url)
    filepath = os.path.join(SAVE_FOLDER, filename)

    if os.path.exists(filepath):
        return

    try:
        r = session.get(pdf_url, stream=True)
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        print("Downloaded:", filename)

    except Exception as e:
        print("Download failed:", e)


def crawl():
    visited_items = set()
    current = START_URL

    page_count = 0
    total_start_time = time.time()

    while current:
        page_count += 1
        page_start_time = time.time()

        print(f"\n===== PAGE {page_count} =====")
        print("URL:", current)

        html = get_page(current)
        if not html:
            break

        items = extract_item_links(html)
        print("Items found:", len(items))

        # Progress bar for items
        for item in tqdm(items, desc=f"Page {page_count}", leave=False):

            if item in visited_items:
                continue

            visited_items.add(item)

            pdfs = extract_pdf_links(item)

            for pdf in pdfs:
                fname = filename_from_url(pdf)

                if TARGET_COURSE in fname:
                    print("\nMATCH FOUND:", fname)
                    download_pdf(pdf)

            time.sleep(DELAY)

        # Page timing
        page_time = time.time() - page_start_time
        total_time = time.time() - total_start_time

        print(f"⏱ Page {page_count} Time: {page_time:.2f} sec")
        print(f"🕒 Total Time: {total_time/60:.2f} min")

        current = get_next_page(html)
        time.sleep(DELAY)


if __name__ == "__main__":
    crawl()
