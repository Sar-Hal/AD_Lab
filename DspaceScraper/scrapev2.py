import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import time

BASE_URL = "http://10.2.0.84:8080"
START_URL = "http://10.2.0.84:8080/dspace/handle/123456789/32"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def get_page(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("Error:", url, e)
        return None


# ✅ ONLY REAL ITEM LINKS
def extract_item_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Must be handle item
        if "/handle/123456789/" in href and "simple-search" not in href:
            full = urljoin(BASE_URL, href)
            links.append(full)

    return list(set(links))


def extract_filename_from_pdf(pdf_url):
    name = pdf_url.split("/")[-1]
    return unquote(name)


def parse_item_page(url):
    html = get_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    pdf_links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "bitstream" in href and ".pdf" in href:
            pdf_links.add(urljoin(BASE_URL, href))

    pdf_links = list(pdf_links)

    filenames = [extract_filename_from_pdf(p) for p in pdf_links]

    return {
        "url": url,
        "pdfs": pdf_links,
        "filenames": filenames
    }


def test_run():
    html = get_page(START_URL)

    items = extract_item_links(html)

    print("Real item links found:", len(items))

    for link in items[:5]:
        print("\nItem:", link)

        data = parse_item_page(link)

        if data:
            for f in data["filenames"]:
                print("PDF:", f)

        time.sleep(1)


if __name__ == "__main__":
    test_run()
