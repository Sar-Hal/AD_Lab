import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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


def extract_item_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        if "/handle/" in a["href"]:
            links.append(urljoin(BASE_URL, a["href"]))

    return list(set(links))


def parse_item_page(url):
    html = get_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h2")
    title = title_tag.text.strip() if title_tag else "Unknown"

    pdf_links = []
    for a in soup.find_all("a", href=True):
        if "bitstream" in a["href"] and ".pdf" in a["href"]:
            pdf_links.append(urljoin(BASE_URL, a["href"]))

    return {
        "title": title,
        "pdfs": pdf_links,
        "url": url
    }


def test_run():
    print("Fetching collection page...")
    html = get_page(START_URL)

    if not html:
        print("Failed to load start page")
        return

    print("Extracting item links...")
    items = extract_item_links(html)

    print("Found item links:", len(items))

    print("\nTesting first 3 items:\n")

    for link in items[:3]:
        print("Opening:", link)
        data = parse_item_page(link)
        print(data)
        print("-" * 50)
        time.sleep(1)


if __name__ == "__main__":
    test_run()
