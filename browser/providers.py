from playwright.sync_api import sync_playwright
from urllib.parse import quote, urlparse


def brave_search(query: str, max_results: int = 10):
    search_url = (
        "https://search.brave.com/search?q="
        + quote(query)
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={
                "width": 1366,
                "height": 900
            },
            locale="en-US",
        )

        page = context.new_page()

        page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(2500)

        print("URL:", page.url)
        print("TITLE:", page.title())

        results = []

        # Brave's result cards
        cards = page.locator(
            'a[href^="http"]'
        )

        count = cards.count()

        print("Candidate links:", count)

        seen = set()

        for i in range(count):

            try:
                link = cards.nth(i)

                href = link.get_attribute("href")
                text = link.inner_text().strip()

                if not href or not text:
                    continue

                parsed = urlparse(href)

                if not parsed.netloc:
                    continue

                if "brave.com" in parsed.netloc:
                    continue

                if href in seen:
                    continue

                seen.add(href)

                results.append({
                    "title": text,
                    "url": href,
                    "source": "brave_browser"
                })

                if len(results) >= max_results:
                    break

            except Exception:
                continue

        page.screenshot(
            path="brave_debug.png",
            full_page=True
        )

        browser.close()

    return {
        "query": query,
        "result_count": len(results),
        "results": results
    }