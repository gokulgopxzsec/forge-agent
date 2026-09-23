import base64
import requests

from bs4 import BeautifulSoup
from urllib.parse import unquote


SEARCH_URL = "https://www.bing.com/search?q={query}"


def decode_bing_url(url: str):
    """
    Convert Bing tracking URLs into the actual destination URL.
    """

    if not url:
        return None

    if "bing.com/ck/a" not in url:
        return url

    try:
        # Extract the `u=` parameter
        marker = "u="

        if marker not in url:
            return url

        encoded = url.split(marker, 1)[1].split("&", 1)[0]

        # Bing commonly uses base64 with an `a1` prefix.
        if encoded.startswith("a1"):
            encoded = encoded[2:]

        # Restore base64 padding
        padding = "=" * (-len(encoded) % 4)
        encoded += padding

        decoded = base64.b64decode(
            encoded
        ).decode(
            "utf-8",
            errors="ignore"
        )

        return decoded

    except Exception:
        return url


def web_search(query: str, max_results: int = 10):

    url = SEARCH_URL.format(
        query=requests.utils.quote(query)
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        results = []

        for item in soup.select("li.b_algo"):

            title_element = item.select_one("h2 a")

            if not title_element:
                continue

            title = title_element.get_text(
                " ",
                strip=True
            )

            raw_url = title_element.get(
                "href"
            )

            destination_url = decode_bing_url(
                raw_url
            )

            snippet_element = item.select_one(
                ".b_caption p"
            )

            snippet = (
                snippet_element.get_text(
                    " ",
                    strip=True
                )
                if snippet_element
                else ""
            )

            if not destination_url:
                continue

            results.append({
                "title": title,
                "url": destination_url,
                "snippet": snippet,
                "source": "bing"
            })

            if len(results) >= max_results:
                break

        return {
            "query": query,
            "result_count": len(results),
            "results": results
        }

    except Exception as e:

        return {
            "query": query,
            "error": str(e),
            "results": []
        }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for information. "
            "Use this when you need to discover "
            "websites, companies, products, "
            "people, or other information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The search query."
                    )
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Maximum number of results "
                        "to return."
                    )
                }
            },
            "required": ["query"]
        }
    }
}