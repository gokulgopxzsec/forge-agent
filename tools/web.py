import requests
from bs4 import BeautifulSoup


def fetch_url(url: str):
    """Fetch and extract readable text from a webpage."""

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "ForgeAgent/0.2"
            }
        )

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup([
            "script",
            "style",
            "noscript"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return {
            "url": url,
            "status_code": response.status_code,
            "content": text[:12000]
        }

    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "fetch_url",
        "description": "Fetch a webpage and extract its readable text.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The complete URL to fetch."
                }
            },
            "required": ["url"]
        }
    }
}