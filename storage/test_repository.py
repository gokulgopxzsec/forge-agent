from storage.database import initialize_database, get_connection
from storage.repositories import (
    create_research_run,
    complete_research_run,
    save_candidate_with_evidence,
)

from search.models import Candidate


if __name__ == "__main__":

    print("=" * 70)
    print("FORGE DATABASE REPOSITORY TEST")
    print("=" * 70)

    initialize_database()

    # Create research run
    run_id = create_research_run(
        "Find hydraulic hose businesses in Houston"
    )

    print()
    print("Research Run ID:", run_id)

    # Create candidate
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
            "industry_terms:hydraulic,hose,hoses"
        ],
    })

    candidate.evidence.append({
        "type": "website_extraction",
        "status": "ok",
        "data": {
            "title": "Hydraulic Components, Systems, and Services - OneHydraulics",
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

    # Save candidate + evidence
    candidate_id = save_candidate_with_evidence(
        candidate,
        run_id,
    )

    print("Candidate ID:", candidate_id)

    # Complete run
    complete_research_run(run_id)

    print("Research run completed.")

    # Verify database
    connection = get_connection()
    cursor = connection.cursor()

    print()
    print("DATABASE CONTENT")
    print("-" * 70)

    cursor.execute(
        "SELECT * FROM research_runs WHERE id = ?",
        (run_id,),
    )

    run = cursor.fetchone()

    print()
    print("RUN:")
    print(dict(run))

    cursor.execute(
        "SELECT * FROM candidates WHERE id = ?",
        (candidate_id,),
    )

    saved_candidate = cursor.fetchone()

    print()
    print("CANDIDATE:")
    print(dict(saved_candidate))

    cursor.execute(
        "SELECT * FROM evidence WHERE candidate_id = ?",
        (candidate_id,),
    )

    evidence_rows = cursor.fetchall()

    print()
    print("EVIDENCE:")

    for row in evidence_rows:
        print(dict(row))

    connection.close()