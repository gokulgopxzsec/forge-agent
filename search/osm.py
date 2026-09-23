import requests


OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def overpass_search(query: str, timeout: int = 45):

    last_error = None

    for server in OVERPASS_SERVERS:

        try:
            print(f"Trying Overpass: {server}")

            response = requests.post(
                server,
                data=query,
                timeout=timeout,
                headers={
                    "User-Agent": "ForgeAgent/0.1"
                }
            )

            print("HTTP:", response.status_code)

            response.raise_for_status()

            data = response.json()

            return {
                "status": "ok",
                "source": "openstreetmap",
                "server": server,
                "result_count": len(data.get("elements", [])),
                "results": data.get("elements", [])
            }

        except Exception as e:

            print("ERROR:", repr(e))
            last_error = repr(e)

    return {
        "status": "error",
        "source": "openstreetmap",
        "result_count": 0,
        "results": [],
        "error": last_error
    }


def search_businesses(
    city: str,
    state: str,
    keywords: list[str],
    limit: int = 50
):

    # Houston approximate bounding box
    south = 29.50
    west = -95.80
    north = 30.20
    east = -95.00

    regex = "|".join(
        keyword.replace("\\", "\\\\").replace('"', '\\"')
        for keyword in keywords
    )

    query = f"""
[out:json][timeout:25];

(
  node["name"~"{regex}",i](
    {south},{west},{north},{east}
  );

  way["name"~"{regex}",i](
    {south},{west},{north},{east}
  );
);

out center tags;
"""

    result = overpass_search(query)

    if result["status"] != "ok":
        return result

    businesses = []

    for element in result["results"][:limit]:

        tags = element.get("tags", {})

        businesses.append({
            "name": tags.get("name"),
            "website": (
                tags.get("website")
                or tags.get("contact:website")
            ),
            "phone": (
                tags.get("phone")
                or tags.get("contact:phone")
            ),
            "street": tags.get("addr:street"),
            "city": tags.get("addr:city"),
            "state": tags.get("addr:state"),
            "postcode": tags.get("addr:postcode"),
            "lat": (
                element.get("lat")
                or element.get("center", {}).get("lat")
            ),
            "lon": (
                element.get("lon")
                or element.get("center", {}).get("lon")
            ),
            "osm_type": element.get("type"),
            "osm_id": element.get("id"),
            "source": "openstreetmap"
        })

    return {
        "status": "ok",
        "source": "openstreetmap",
        "result_count": len(businesses),
        "results": businesses
    }