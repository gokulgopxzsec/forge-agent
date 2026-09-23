from search.models import Candidate
from ai.qualify import qualify_candidate


if __name__ == "__main__":

    candidate = Candidate(
        name="OneHydraulics",
        website="https://www.onehydraulics.com/",
        phone="281-941-2310",
        city="Houston",
        state="Texas",
        source="openstreetmap",
        source_id="node:14125868766",
        status="enriched",
    )

    candidate.evidence.append({
        "type": "website_verification",
        "url": "https://www.onehydraulics.com/",
        "score": 85,
        "evidence": [
            "company_name_in_title",
            "city_found",
            "industry_terms:hydraulic,hose,hoses",
        ],
    })

    candidate.evidence.append({
        "type": "website_extraction",
        "status": "ok",
        "data": {
            "title": (
                "Hydraulic Components, Systems, "
                "and Services - OneHydraulics"
            ),
            "description": (
                "OneHydraulics is a provider for hydraulic "
                "components, systems, and services in Houston, TX."
            ),
            "phones": [
                "281-941-2310"
            ],
            "emails": [
                "sales@onehydraulics.com"
            ],
            "industry_terms": [
                "hydraulic",
                "hydraulics",
                "hose",
                "hoses",
                "fluid power",
                "pneumatic",
                "fittings",
                "valves",
            ],
        },
    })

    print("=" * 70)
    print("FORGE QWEN3 QUALIFICATION")
    print("=" * 70)

    print()
    print("Analyzing:", candidate.name)

    result = qualify_candidate(candidate)

    print()
    print("RESULT")
    print("-" * 70)

    print()
    print("Industry:")
    print(result.get("industry"))

    print()
    print("Business Type:")
    print(result.get("business_type"))

    print()
    print("Hose Relevance:")
    print(result.get("hose_relevance"))

    print()
    print("HorseTrace Fit:")
    print(result.get("potential_horsetrace_fit"))

    print()
    print("Reasoning:")
    print(result.get("reasoning"))

    print()
    print("Outreach Angle:")
    print(result.get("outreach_angle"))

    print()
    print("Confidence:")
    print(result.get("confidence"))

    print()
    print("RAW JSON")
    print("-" * 70)

    print(result)