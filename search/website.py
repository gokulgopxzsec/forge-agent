import base64
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import (
    quote,
    urlparse,
    parse_qs,
    unquote,
)


# ============================================================
# CONFIG
# ============================================================

REQUEST_TIMEOUT = 8

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# Domains that are almost never the actual company website.
BLOCKED_DOMAINS = {
    "google.com",
    "www.google.com",
    "bing.com",
    "www.bing.com",
    "yahoo.com",
    "www.yahoo.com",
    "youtube.com",
    "www.youtube.com",
    "facebook.com",
    "www.facebook.com",
    "instagram.com",
    "www.instagram.com",
    "linkedin.com",
    "www.linkedin.com",
    "wikipedia.org",
    "www.wikipedia.org",
    "amazon.com",
    "www.amazon.com",
    "amazon.in",
    "www.amazon.in",
    "flipkart.com",
    "www.flipkart.com",
    "indiamart.com",
    "www.indiamart.com",
    "myntra.com",
    "www.myntra.com",
    "moglix.com",
    "www.moglix.com",
}


# ============================================================
# URL HELPERS
# ============================================================

def decode_bing_url(url: str) -> str:
    """
    Decode Bing tracking URLs such as:

    https://www.bing.com/ck/a?...&u=a1aHR0cHM6Ly9leGFtcGxlLmNvbQ...

    into the actual destination URL.
    """

    if not url:
        return ""

    if "bing.com/ck/a" not in url:
        return url

    try:
        parsed = urlparse(url)

        params = parse_qs(parsed.query)

        encoded = params.get("u", [None])[0]

        if not encoded:
            return url

        if encoded.startswith("a1"):
            encoded = encoded[2:]

        # Base64 padding
        encoded += "=" * (-len(encoded) % 4)

        decoded = base64.urlsafe_b64decode(
            encoded
        ).decode("utf-8", errors="ignore")

        if decoded.startswith(("http://", "https://")):
            return decoded

    except Exception:
        pass

    return url


def normalize_url(url: str) -> str:
    """
    Normalize a URL into a clean absolute URL.
    """

    if not url:
        return ""

    url = decode_bing_url(url)

    url = unquote(url).strip()

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url.rstrip("/")


def get_domain(url: str) -> str:
    """
    Return hostname without www.
    """

    try:
        hostname = urlparse(url).hostname

        if not hostname:
            return ""

        return hostname.lower().removeprefix("www.")

    except Exception:
        return ""


# ============================================================
# COMPANY NAME NORMALIZATION
# ============================================================

def normalize_company_name(name: str) -> str:
    """
    Convert company name into a normalized comparison string.

    Example:

        "One-Hydraulics, LLC"
        -> "one hydraulics"

    """

    if not name:
        return ""

    name = name.lower()

    # Remove common legal suffixes
    name = re.sub(
        r"\b(inc|incorporated|llc|l\.l\.c|corp|corporation|co|company|ltd)\b",
        " ",
        name,
    )

    # Replace punctuation with spaces
    name = re.sub(r"[^a-z0-9]+", " ", name)

    # Collapse whitespace
    name = re.sub(r"\s+", " ", name)

    return name.strip()


def company_tokens(name: str) -> list[str]:
    """
    Return meaningful company-name tokens.
    """

    normalized = normalize_company_name(name)

    tokens = normalized.split()

    # Ignore extremely common generic terms.
    stopwords = {
        "the",
        "and",
        "of",
        "for",
        "llc",
        "inc",
        "company",
        "corp",
        "corporation",
    }

    return [
        token
        for token in tokens
        if token not in stopwords and len(token) >= 3
    ]


# ============================================================
# DOMAIN GENERATION
# ============================================================

def generate_domain_candidates(company_name: str) -> list[str]:
    """
    Generate likely domains from a company name.

    Example:

        One Hydraulics

    becomes candidates such as:

        onehydraulics.com
        onehydraulics.net
        onehydraulics.us
        one-hydraulics.com
        onehydraulicsusa.com
        onehydraulics.us
    """

    normalized = normalize_company_name(company_name)

    if not normalized:
        return []

    words = normalized.split()

    compact = "".join(words)
    hyphenated = "-".join(words)

    candidates = []

    # Highest probability domains first.
    bases = [
        compact,
        hyphenated,
        compact + "usa",
        compact + "us",
        compact + "usa",
        hyphenated + "usa",
    ]

    extensions = [
        ".com",
        ".net",
        ".us",
    ]

    for base in bases:
        for extension in extensions:
            domain = base + extension

            if domain not in candidates:
                candidates.append(domain)

    return candidates


# ============================================================
# WEBSITE FETCH
# ============================================================

def fetch_website(url: str) -> dict:
    """
    Fetch a website and extract basic evidence.

    Returns structured information rather than just HTML.
    """

    url = normalize_url(url)

    if not url:
        return {
            "status": "error",
            "url": url,
            "error": "empty_url",
        }

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        final_url = response.url

        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        result = {
            "status": "ok",
            "requested_url": url,
            "final_url": final_url,
            "status_code": response.status_code,
            "content_type": content_type,
            "domain": get_domain(final_url),
        }

        if "text/html" not in content_type:
            result["title"] = ""
            result["text"] = ""
            return result

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove things that add noise.
        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
            ]
        ):
            element.decompose()

        title = ""

        if soup.title:
            title = soup.title.get_text(
                " ",
                strip=True,
            )

        text = soup.get_text(
            " ",
            strip=True,
        )

        # Keep evidence bounded.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        text = text[:20000]

        result["title"] = title[:500]
        result["text"] = text

        return result

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "url": url,
            "error": "timeout",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "url": url,
            "error": str(exc),
        }

    except Exception as exc:
        return {
            "status": "error",
            "url": url,
            "error": str(exc),
        }


# ============================================================
# WEBSITE RELEVANCE
# ============================================================

def score_website(
    company_name: str,
    website: dict,
    city: str | None = None,
    state: str | None = None,
) -> dict:
    """
    Score how likely a website belongs to the requested company.

    This is deterministic.

    Qwen should be used later for deeper semantic verification.
    """

    if website.get("status") != "ok":
        return {
            "score": 0,
            "matched_tokens": [],
            "evidence": [],
        }

    domain = website.get("domain", "").lower()

    if domain in BLOCKED_DOMAINS:
        return {
            "score": 0,
            "matched_tokens": [],
            "evidence": ["blocked_domain"],
        }

    title = website.get("title", "").lower()
    text = website.get("text", "").lower()

    combined = f"{title} {text}"

    tokens = company_tokens(company_name)

    matched_tokens = []

    for token in tokens:
        if token in combined:
            matched_tokens.append(token)

    score = 0
    evidence = []

    # --------------------------------------------------------
    # Company name evidence
    # --------------------------------------------------------

    if normalize_company_name(company_name) in normalize_company_name(
        website.get("title", "")
    ):
        score += 50
        evidence.append("company_name_in_title")

    elif len(matched_tokens) >= max(1, len(tokens) // 2):
        score += 30
        evidence.append("company_tokens_found")

    # --------------------------------------------------------
    # Business/location evidence
    # --------------------------------------------------------

    if city:
        city_lower = city.lower()

        if city_lower in combined:
            score += 15
            evidence.append("city_found")

    if state:
        state_lower = state.lower()

        if state_lower in combined:
            score += 10
            evidence.append("state_found")

    # --------------------------------------------------------
    # Industry evidence
    # --------------------------------------------------------

    industry_terms = [
        "hydraulic",
        "hose",
        "hoses",
        "hydraulics",
        "fluid power",
        "industrial hose",
        "hose assembly",
        "hose repair",
        "fittings",
        "fitting",
        "pneumatic",
    ]

    industry_matches = []

    for term in industry_terms:
        if term in combined:
            industry_matches.append(term)

    if industry_matches:
        score += min(
            20,
            len(industry_matches) * 5,
        )

        evidence.append(
            "industry_terms:" + ",".join(industry_matches[:5])
        )

    # --------------------------------------------------------
    # Cap score
    # --------------------------------------------------------

    score = min(score, 100)

    return {
        "score": score,
        "matched_tokens": matched_tokens,
        "evidence": evidence,
    }


# ============================================================
# DIRECT WEBSITE DISCOVERY
# ============================================================

def discover_direct_website(
    company_name: str,
    city: str | None = None,
    state: str | None = None,
) -> dict:
    """
    Try likely domains directly.

    This should be the first website-discovery method.
    """

    domains = generate_domain_candidates(company_name)

    candidates = []

    for domain in domains:

        # HTTPS first.
        url = f"https://{domain}"

        result = fetch_website(url)

        if result.get("status") != "ok":
            continue

        score = score_website(
            company_name,
            result,
            city,
            state,
        )

        candidate = {
            "company": company_name,
            "url": result.get("final_url"),
            "domain": result.get("domain"),
            "title": result.get("title"),
            "status_code": result.get("status_code"),
            "score": score["score"],
            "evidence": score["evidence"],
            "matched_tokens": score["matched_tokens"],
            "source": "direct_domain",
        }

        candidates.append(candidate)

        # A strong match means we don't need to test
        # every remaining domain.
        if score["score"] >= 70:
            break

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    best = candidates[0] if candidates else None

    return {
        "company": company_name,
        "method": "direct_domain",
        "candidate_count": len(candidates),
        "best": best,
        "candidates": candidates,
    }


# ============================================================
# BING SEARCH FALLBACK
# ============================================================

def extract_domains_from_bing(
    query: str,
    max_results: int = 10,
):
    """
    Bing fallback.

    IMPORTANT:
    Bing results are treated as candidates only.
    They are NOT considered verified websites.
    """

    search_url = (
        "https://www.bing.com/search?q="
        + quote(query)
    )

    try:
        response = requests.get(
            search_url,
            timeout=15,
            headers=HEADERS,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        results = []

        for item in soup.select("li.b_algo"):

            link = item.select_one("h2 a")

            if not link:
                continue

            title = link.get_text(
                " ",
                strip=True,
            )

            raw_url = link.get("href")

            if not raw_url:
                continue

            url = normalize_url(raw_url)

            domain = get_domain(url)

            if domain in BLOCKED_DOMAINS:
                continue

            snippet = ""

            caption = item.select_one(
                ".b_caption p"
            )

            if caption:
                snippet = caption.get_text(
                    " ",
                    strip=True,
                )

            results.append(
                {
                    "title": title,
                    "url": url,
                    "domain": domain,
                    "snippet": snippet,
                    "source": "bing",
                }
            )

            if len(results) >= max_results:
                break

        return results

    except Exception as exc:
        return [
            {
                "error": str(exc),
                "source": "bing",
            }
        ]


# ============================================================
# BING RELEVANCE FILTER
# ============================================================

def filter_search_results(
    company_name: str,
    results: list[dict],
):
    """
    Filter obviously irrelevant search results.

    Search engines can return unrelated pages.
    Never trust raw ranking.
    """

    tokens = company_tokens(company_name)

    filtered = []

    for result in results:

        if result.get("error"):
            continue

        title = result.get(
            "title",
            "",
        ).lower()

        snippet = result.get(
            "snippet",
            "",
        ).lower()

        domain = result.get(
            "domain",
            "",
        ).lower()

        combined = (
            f"{title} "
            f"{snippet} "
            f"{domain}"
        )

        matched = [
            token
            for token in tokens
            if token in combined
        ]

        if not matched:
            continue

        # At least one meaningful company token
        # should appear.
        result["matched_tokens"] = matched

        result["relevance_score"] = (
            len(matched) / max(len(tokens), 1)
        ) * 100

        filtered.append(result)

    filtered.sort(
        key=lambda item: item["relevance_score"],
        reverse=True,
    )

    return filtered


# ============================================================
# COMPLETE DISCOVERY
# ============================================================

def discover_website(
    company_name: str,
    city: str | None = None,
    state: str | None = None,
):
    """
    Complete website discovery pipeline.

    Order:

        1. Direct domain discovery
        2. Bing fallback
        3. Bing relevance filtering

    IMPORTANT:
    A Bing result is still only a candidate.
    """

    # --------------------------------------------------------
    # STEP 1
    # Direct domain discovery
    # --------------------------------------------------------

    direct = discover_direct_website(
        company_name,
        city,
        state,
    )

    if direct["best"]:
        return {
            "company": company_name,
            "status": "verified_candidate",
            "method": "direct_domain",
            "best": direct["best"],
            "direct_candidates": direct["candidates"],
            "search_candidates": [],
        }

    # --------------------------------------------------------
    # STEP 2
    # Search fallback
    # --------------------------------------------------------

    query_parts = [
        f'"{company_name}"',
    ]

    if city:
        query_parts.append(
            f'"{city}"'
        )

    if state:
        query_parts.append(
            f'"{state}"'
        )

    query = " ".join(query_parts)

    search_results = extract_domains_from_bing(
        query,
        max_results=10,
    )

    filtered = filter_search_results(
        company_name,
        search_results,
    )

    return {
        "company": company_name,
        "status": (
            "search_candidates"
            if filtered
            else "not_found"
        ),
        "method": "bing_fallback",
        "best": (
            filtered[0]
            if filtered
            else None
        ),
        "direct_candidates": [],
        "search_candidates": filtered,
    }