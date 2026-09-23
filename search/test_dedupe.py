from search.models import Candidate
from search.dedupe import deduplicate_candidates


if __name__ == "__main__":

    candidates = [

        Candidate(
            name="OneHydraulics",
            city="Houston",
            state="Texas",
            website="https://www.onehydraulics.com/",
            phone="281-941-2310",
            source="openstreetmap",
            source_id="node:14125868766",
        ),

        # Same company, different source
        Candidate(
            name="OneHydraulics",
            city="Houston",
            state="Texas",
            website="https://onehydraulics.com",
            source="bing",
            source_id="search:123",
        ),

        # Another company
        Candidate(
            name="Hose Master",
            city="Houston",
            state="Texas",
            website="https://www.hosemaster.com/",
            source="openstreetmap",
            source_id="way:364584217",
        ),
    ]

    print("=" * 70)
    print("FORGE DEDUPLICATION TEST")
    print("=" * 70)

    print()
    print("Before:", len(candidates))

    unique = deduplicate_candidates(candidates)

    print("After:", len(unique))

    print()

    for i, candidate in enumerate(unique, 1):

        print(f"[{i}] {candidate.name}")
        print(f"    Website: {candidate.website}")
        print(f"    Phone: {candidate.phone}")
        print(f"    City: {candidate.city}")
        print(f"    Source: {candidate.source}")
        print()