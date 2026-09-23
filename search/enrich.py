from search.models import Candidate
from search.website import discover_website
from search.extract import extract_business_data


def enrich_candidate(
    candidate: Candidate,
) -> Candidate:
    """
    Enrich a discovered candidate with:

    1. Website discovery
    2. Website verification
    3. Business information extraction
    """

    print(
        f"\n[WEBSITE] "
        f"Resolving: {candidate.name}"
    )

    # --------------------------------------------------------
    # STEP 1
    # Find website
    # --------------------------------------------------------

    discovery = discover_website(
        company_name=candidate.name,
        city=candidate.city,
        state=candidate.state,
    )

    best = discovery.get("best")

    if not best:
        candidate.status = "website_not_found"

        candidate.evidence.append({
            "type": "website_discovery",
            "status": "not_found",
        })

        return candidate

    website_url = best.get("url")

    candidate.website = website_url

    print(
        f"[WEBSITE] "
        f"Found: {website_url}"
    )

    # --------------------------------------------------------
    # STEP 2
    # Website verification evidence
    # --------------------------------------------------------

    candidate.evidence.append({
        "type": "website_verification",
        "method": discovery.get("method"),
        "url": website_url,
        "score": best.get("score"),
        "evidence": best.get("evidence", []),
    })

    # --------------------------------------------------------
    # STEP 3
    # Extract business intelligence
    # --------------------------------------------------------

    print(
        f"[EXTRACT] "
        f"{website_url}"
    )

    extracted = extract_business_data(
        website_url
    )

    if extracted.get("status") != "ok":

        candidate.status = (
            "website_extraction_failed"
        )

        candidate.evidence.append({
            "type": "website_extraction",
            "status": "error",
            "error": extracted.get(
                "error",
                "unknown_error",
            ),
        })

        return candidate

    # --------------------------------------------------------
    # STEP 4
    # Attach extracted intelligence
    # --------------------------------------------------------

    business = extracted.get(
        "business",
        {},
    )

    candidate.evidence.append({
        "type": "website_extraction",
        "status": "ok",
        "data": business,
    })

    # --------------------------------------------------------
    # STEP 5
    # Update candidate fields where appropriate
    # --------------------------------------------------------

    phones = business.get(
        "phones",
        [],
    )

    emails = business.get(
        "emails",
        [],
    )

    addresses = business.get(
        "addresses",
        [],
    )

    if not candidate.phone and phones:
        candidate.phone = phones[0]

    # Save extracted information as evidence
    # rather than expanding Candidate endlessly.
    candidate.status = "enriched"

    return candidate