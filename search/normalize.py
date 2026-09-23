from search.models import Candidate


def normalize_osm(results: list[dict]) -> list[Candidate]:

    candidates = []

    for item in results:

        if not item.get("name"):
            continue

        candidate = Candidate(
            name=item["name"],
            website=item.get("website"),
            phone=item.get("phone"),
            street=item.get("street"),
            city=item.get("city"),
            state=item.get("state"),
            postcode=item.get("postcode"),
            source="openstreetmap",
            source_id=(
                f"{item.get('osm_type')}:"
                f"{item.get('osm_id')}"
            )
        )

        candidates.append(candidate)

    return candidates