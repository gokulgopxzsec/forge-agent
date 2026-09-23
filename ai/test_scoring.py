from search.models import Candidate
from ai.qualify import qualify_candidate
from ai.scoring import calculate_lead_score


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
            "social": [
                "https://www.linkedin.com/company/onehydraulics"
            ],
        },
    })

    print("=" * 70)
    print("FORGE LEAD ANALYSIS")
    print("=" * 70)

    print()
    print("Company:", candidate.name)

    print()
    print("[1] QWEN3 ANALYSIS")
    print("-" * 70)

    analysis = qualify_candidate(candidate)

    for key, value in analysis.items():
        print(f"{key}: {value}")

    print()
    print("[2] DETERMINISTIC SCORE")
    print("-" * 70)

    scoring = calculate_lead_score(
        candidate,
        analysis,
    )

    print()
    print("Score:", scoring["score"], "/ 100")

    print()
    print("Reasons:")

    for reason in scoring["reasons"]:
        print(" -", reason)