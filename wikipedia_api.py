import requests

import cache

API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "WikipediaChainFinder/1.0 (CMS430-AI project)"}
TIMEOUT = 15

# Initialize the cache database on module load
cache.init_db()


def get_forward_links(title: str) -> set[str]:
    """Return the set of article titles that the given article links to."""
    # Check cache first
    cached = cache.get_cached_links(title, "forward")
    if cached is not None:
        return cached

    links = set()
    params = {
        "action": "query",
        "titles": title,
        "prop": "links",
        "pllimit": "max",
        "plnamespace": 0,
        "format": "json",
    }

    while True:
        resp = _get(params)
        pages = resp.get("query", {}).get("pages", {})
        for page in pages.values():
            for link in page.get("links", []):
                links.add(link["title"])

        if "continue" not in resp:
            break
        params.update(resp["continue"])

    # Cache the result before returning
    cache.cache_links(title, links, "forward")
    return links


def get_backward_links(title: str) -> set[str]:
    """Return the set of article titles that link to the given article."""
    # Check cache first
    cached = cache.get_cached_links(title, "backward")
    if cached is not None:
        return cached

    links = set()
    params = {
        "action": "query",
        "titles": title,
        "prop": "linkshere",
        "lhlimit": "max",
        "lhnamespace": 0,
        "format": "json",
    }

    while True:
        resp = _get(params)
        pages = resp.get("query", {}).get("pages", {})
        for page in pages.values():
            for link in page.get("linkshere", []):
                links.add(link["title"])

        if "continue" not in resp:
            break
        params.update(resp["continue"])

    # Cache the result before returning
    cache.cache_links(title, links, "backward")
    return links


def article_exists(title: str) -> bool:
    """Return True if the given title resolves to a valid Wikipedia article."""
    params = {
        "action": "query",
        "titles": title,
        "format": "json",
    }
    resp = _get(params)
    pages = resp.get("query", {}).get("pages", {})
    for page_id in pages:
        if page_id == "-1" or "missing" in pages[page_id]:
            return False
    return True


def _get(params: dict) -> dict:
    """Make a GET request to the Wikipedia API and return the parsed JSON."""
    try:
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.ConnectionError:
        raise RuntimeError(f"Could not connect to Wikipedia API at {API_URL}")
    except requests.Timeout:
        raise RuntimeError("Wikipedia API request timed out")
    except requests.HTTPError as e:
        raise RuntimeError(f"Wikipedia API returned HTTP {e.response.status_code}")

    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError("Wikipedia API returned invalid JSON")

    if "error" in data:
        raise RuntimeError(f"Wikipedia API error: {data['error'].get('info', 'unknown')}")

    return data
