from search.models import Candidate
from search.enrich import enrich_candidate


if __name__ == "__main__":

    candidate = Candidate(
        name="OneHydraulics",
        city="Houston",
        state="Texas",
        source="openstreetmap",
        source_id="node:14125868766",
    )

    result = enrich_candidate(
        candidate
    )

    print()
    print("=" * 70)
    print("FORGE ENRICHMENT RESULT")
    print("=" * 70)

    print()

    print("Name:", result.name)
    print("Website:", result.website)
    print("Phone:", result.phone)
    print("Status:", result.status)

    print()
    print("EVIDENCE")
    print("-" * 70)

    for item in result.evidence:

        print()
        print(
            "Type:",
            item.get("type"),
        )

        print(
            "Status:",
            item.get("status"),
        )

        if "data" in item:
            data = item["data"]

            print(
                "Title:",
                data.get("title"),
            )

            print(
                "Description:",
                data.get("description"),
            )

            print(
                "Emails:",
                data.get("emails"),
            )

            print(
                "Phones:",
                data.get("phones"),
            )

            print(
                "Industry:",
                data.get("industry_terms"),
            )