from playwright.sync_api import sync_playwright
from urllib.parse import quote, urlparse, parse_qs


def clean_google_url(href):
    """Extract the real destination URL from Google links."""

    if not href:
        return None

    if href.startswith("/url?"):
        parsed = urlparse(href)
        params = parse_qs(parsed.query)

        if "q" in params:
            return params["q"][0]

        if "url" in params:
            return params["url"][0]

    if href.startswith("http"):
        return href

    return None


def browser_search(query: str, max_results: int = 10):

    search_url = (
        "https://www.google.com/search?q="
        + quote(query)
        + "&num=20"
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            viewport={
                "width": 1366,
                "height": 900
            },
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        print("Opening:", search_url)

        page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(3000)

        print("Final URL:", page.url)
        print("Title:", page.title())

        # Save what the browser actually received.
        page.screenshot(
            path="google_debug.png",
            full_page=True
        )

        with open(
            "google_browser_debug.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(page.content())

        results = []

        # Google organic results normally contain h3 headings.
        headings = page.locator("h3")

        print("H3 count:", headings.count())

        for i in range(headings.count()):

            try:
                heading = headings.nth(i)

                title = heading.inner_text().strip()

                # The result title is normally inside an <a>.
                link = heading.locator("xpath=ancestor::a[1]")

                if link.count() == 0:
                    continue

                href = link.get_attribute("href")

                href = clean_google_url(href)

                if not href:
                    continue

                parsed = urlparse(href)

                if parsed.netloc.endswith("google.com"):
                    continue

                # Try to get surrounding result text.
                try:
                    container = heading.locator(
                        "xpath=ancestor::div[contains(@class,'MjjYud')][1]"
                    )

                    snippet = container.inner_text().strip()

                except Exception:
                    snippet = ""

                results.append({
                    "title": title,
                    "url": href,
                    "snippet": snippet,
                    "source": "google_browser"
                })

                if len(results) >= max_results:
                    break

            except Exception as e:
                print("Result extraction error:", e)

        browser.close()

    return {
        "query": query,
        "result_count": len(results),
        "results": results
    }