import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    )
}


# ============================================================
# FETCH
# ============================================================

def fetch_page(url: str) -> dict:
    """
    Download a webpage and return HTML + metadata.
    """

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        response.raise_for_status()

        return {
            "status": "ok",
            "requested_url": url,
            "final_url": response.url,
            "status_code": response.status_code,
            "html": response.text,
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error": "timeout",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(text: str) -> str:
    """
    Normalize whitespace.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def unique(values: list[str]) -> list[str]:
    """
    Remove duplicates while preserving order.
    """

    result = []

    seen = set()

    for value in values:

        value = value.strip()

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(value)

    return result


# ============================================================
# CONTACT EXTRACTION
# ============================================================

def extract_emails(soup: BeautifulSoup) -> list[str]:
    """
    Extract email addresses from visible page text
    and mailto links.
    """

    emails = []

    # mailto links
    for link in soup.select("a[href^='mailto:']"):

        href = link.get("href", "")

        email = href.replace(
            "mailto:",
            "",
        ).split("?")[0]

        emails.append(email)

    # Visible text
    text = soup.get_text(" ")

    matches = re.findall(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        flags=re.IGNORECASE,
    )

    emails.extend(matches)

    return unique(emails)


def extract_phones(soup: BeautifulSoup) -> list[str]:
    """
    Extract phone numbers from tel links and page text.
    """

    phones = []

    # tel links
    for link in soup.select("a[href^='tel:']"):

        href = link.get("href", "")

        phone = href.replace(
            "tel:",
            "",
        ).strip()

        phones.append(phone)

    # Visible text
    text = soup.get_text(" ")

    matches = re.findall(
        r"(?:\+?1[\s.-]?)?"
        r"(?:\(?\d{3}\)?[\s.-]?)"
        r"\d{3}[\s.-]\d{4}",
        text,
    )

    phones.extend(matches)

    return unique(phones)


# ============================================================
# SOCIAL LINKS
# ============================================================

def extract_social_links(
    soup: BeautifulSoup,
    base_url: str,
) -> list[str]:

    platforms = (
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "youtube.com",
        "twitter.com",
        "x.com",
        "tiktok.com",
    )

    links = []

    for anchor in soup.find_all("a", href=True):

        href = anchor["href"]

        absolute = urljoin(
            base_url,
            href,
        )

        domain = urlparse(
            absolute
        ).netloc.lower()

        if any(
            platform in domain
            for platform in platforms
        ):
            links.append(absolute)

    return unique(links)


# ============================================================
# CONTACT / IMPORTANT PAGES
# ============================================================

def extract_page_links(
    soup: BeautifulSoup,
    base_url: str,
) -> dict:

    pages = {
        "contact": [],
        "about": [],
        "services": [],
        "products": [],
        "locations": [],
    }

    keywords = {
    "contact": [
        "contact",
        "contact us",
        "get in touch",
        "reach us",
    ],

    "about": [
        "about",
        "about us",
        "who we are",
        "our company",
        "our story",
    ],

    "services": [
        "our services",
        "services",
        "what we do",
        "solutions",
        "capabilities",
    ],

    "products": [
        "products",
        "product",
        "catalog",
        "shop",
        "solutions",
    ],

    "locations": [
        "locations",
        "location",
        "our locations",
        "find us",
    ],
}

    for anchor in soup.find_all(
        "a",
        href=True,
    ):

        text = clean_text(
            anchor.get_text(" ")
        ).lower()

        href = anchor["href"]

        absolute = urljoin(
            base_url,
            href,
        )

        for page_type, words in keywords.items():

            if any(
                word in text
                for word in words
            ):
                pages[page_type].append(
                    absolute
                )

    for page_type in pages:
        pages[page_type] = unique(
            pages[page_type]
        )[:5]

    return pages


# ============================================================
# ADDRESS EXTRACTION
# ============================================================

def extract_address(
    soup: BeautifulSoup,
) -> list[str]:

    addresses = []

    # Schema.org address
    for element in soup.select(
        '[itemprop="address"]'
    ):

        text = clean_text(
            element.get_text(" ")
        )

        if text:
            addresses.append(text)

    # Common address elements
    for element in soup.select(
        "address"
    ):

        text = clean_text(
            element.get_text(" ")
        )

        if text:
            addresses.append(text)

    return unique(addresses)


# ============================================================
# META DATA
# ============================================================

def extract_metadata(
    soup: BeautifulSoup,
) -> dict:

    title = ""

    if soup.title:
        title = clean_text(
            soup.title.get_text(" ")
        )

    description = ""

    meta_description = soup.find(
        "meta",
        attrs={
            "name": "description"
        },
    )

    if meta_description:
        description = clean_text(
            meta_description.get(
                "content",
                "",
            )
        )

    # OpenGraph description fallback
    if not description:

        og_description = soup.find(
            "meta",
            attrs={
                "property": "og:description"
            },
        )

        if og_description:
            description = clean_text(
                og_description.get(
                    "content",
                    "",
                )
            )

    return {
        "title": title,
        "description": description,
    }


# ============================================================
# HEADINGS
# ============================================================

def extract_headings(
    soup: BeautifulSoup,
) -> list[str]:

    headings = []

    for element in soup.find_all(
        ["h1", "h2", "h3"]
    ):

        text = clean_text(
            element.get_text(" ")
        )

        if text:
            headings.append(text)

    return unique(headings)[:50]


# ============================================================
# BUSINESS KEYWORDS
# ============================================================

INDUSTRY_TERMS = [
    "hydraulic",
    "hydraulics",
    "hose",
    "hoses",
    "hose assembly",
    "hose repair",
    "industrial hose",
    "fluid power",
    "pneumatic",
    "fittings",
    "fitting",
    "valves",
    "hydraulic systems",
    "hydraulic equipment",
    "mobile hose",
    "hose fabrication",
]


def extract_industry_terms(
    text: str,
) -> list[str]:

    text_lower = text.lower()

    found = []

    for term in INDUSTRY_TERMS:

        if term.lower() in text_lower:
            found.append(term)

    return found


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_business_data(
    url: str,
) -> dict:

    page = fetch_page(url)

    if page["status"] != "ok":

        return {
            "status": "error",
            "url": url,
            "error": page.get(
                "error",
                "unknown_error",
            ),
        }

    final_url = page["final_url"]

    soup = BeautifulSoup(
        page["html"],
        "html.parser",
    )

    # Remove noisy elements
    for element in soup.find_all(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        element.decompose()

    metadata = extract_metadata(
        soup
    )

    headings = extract_headings(
        soup
    )

    text = clean_text(
        soup.get_text(" ")
    )

    # Keep output bounded.
    text = text[:30000]

    emails = extract_emails(
        soup
    )

    phones = extract_phones(
        soup
    )

    social_links = extract_social_links(
        soup,
        final_url,
    )

    important_pages = extract_page_links(
        soup,
        final_url,
    )

    addresses = extract_address(
        soup
    )

    industry_terms = extract_industry_terms(
        text
    )

    return {
        "status": "ok",

        "website": {
            "requested_url": url,
            "final_url": final_url,
            "domain": urlparse(
                final_url
            ).netloc.lower(),
            "status_code": page[
                "status_code"
            ],
        },

        "business": {
            "title": metadata["title"],
            "description": metadata[
                "description"
            ],
            "headings": headings,
            "addresses": addresses,
            "phones": phones,
            "emails": emails,
            "social_links": social_links,
            "important_pages": important_pages,
            "industry_terms": industry_terms,
        },

        "evidence": {
            "page_text": text,
            "title": metadata["title"],
            "description": metadata[
                "description"
            ],
            "headings": headings,
        },
    }


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    url = (
        "https://www.onehydraulics.com/"
    )

    result = extract_business_data(
        url
    )

    print("=" * 70)
    print("FORGE WEBSITE EXTRACTION")
    print("=" * 70)

    print()

    print("Status:", result["status"])

    if result["status"] == "ok":

        website = result["website"]
        business = result["business"]

        print()
        print("WEBSITE")
        print("-" * 70)
        print(
            "URL:",
            website["final_url"],
        )
        print(
            "Domain:",
            website["domain"],
        )
        print(
            "HTTP:",
            website["status_code"],
        )

        print()
        print("BUSINESS")
        print("-" * 70)
        print(
            "Title:",
            business["title"],
        )

        print(
            "Description:",
            business["description"],
        )

        print(
            "Phones:",
            business["phones"],
        )

        print(
            "Emails:",
            business["emails"],
        )

        print(
            "Addresses:",
            business["addresses"],
        )

        print(
            "Industry:",
            business["industry_terms"],
        )

        print(
            "Social:",
            business["social_links"],
        )

        print()
        print("IMPORTANT PAGES")
        print("-" * 70)

        for page_type, links in business[
            "important_pages"
        ].items():

            print(
                f"{page_type}:",
                links,
            )

        print()
        print("HEADINGS")
        print("-" * 70)

        for heading in business[
            "headings"
        ][:20]:

            print("-", heading)