import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "http://10.2.0.84:8080/dspace/handle/123456789/"

START = 1
END = 400   # increase later if needed

DELAY = 0.2

KEYWORDS = [
    # Faculty / School Level
    "humanities",
    "humanity",
    "arts",
    "management",
    "business",
    "social",

    # Course Domain
    "leadership",
    "team",
    "organization",
    "organisational",
    "hr",
    "behaviour",
    "behavior"
]

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def get_title(html):
    soup = BeautifulSoup(html, "html.parser")

    if soup.title:
        return soup.title.text.strip()

    h = soup.find(["h1", "h2", "h3"])
    if h:
        return h.text.strip()

    return "NO TITLE"


def check_handle(num):

    url = BASE_URL + str(num)

    try:
        r = session.get(url, timeout=10)

        if r.status_code != 200:
            return None

        title = get_title(r.text)

        return (url, title)

    except:
        return None


print("\n===== HANDLE ENUMERATION START =====\n")

for i in range(START, END + 1):

    result = check_handle(i)

    if result:
        url, title = result

        title_lower = title.lower()

        if any(k in title_lower for k in KEYWORDS):
            print("\n🔥 POSSIBLE MATCH FOUND")
            print("Handle:", url)
            print("Title :", title)

        else:
            print("Checked:", i, "|", title)

    time.sleep(DELAY)

print("\n===== DONE =====")
