from search.models import Candidate


def calculate_lead_score(
    candidate: Candidate,
    analysis: dict,
) -> dict:

    score = 0
    reasons = []

    # Website exists
    if candidate.website:
        score += 20
        reasons.append("website_exists")

    # Website was verified
    verification = any(
        evidence.get("type") == "website_verification"
        for evidence in candidate.evidence
    )

    if verification:
        score += 15
        reasons.append("website_verified")

    # Geography
    if candidate.city:
        score += 15
        reasons.append("location_identified")

    # Industry
    hose_relevance = analysis.get("hose_relevance")

    if hose_relevance == "high":
        score += 15
        reasons.append("high_hose_relevance")

    elif hose_relevance == "medium":
        score += 8
        reasons.append("medium_hose_relevance")

    # HorseTrace fit
    fit = analysis.get("potential_horsetrace_fit")

    if fit == "high":
        score += 15
        reasons.append("high_horsetrace_fit")

    elif fit == "medium":
        score += 8
        reasons.append("medium_horsetrace_fit")

    # Contact information
    if candidate.phone:
        score += 5
        reasons.append("phone_available")

    # Email from evidence
    has_email = False

    for evidence in candidate.evidence:

        if evidence.get("type") != "website_extraction":
            continue

        data = evidence.get("data", {})

        if data.get("emails"):
            has_email = True
            break

    if has_email:
        score += 5
        reasons.append("email_available")

    # Social presence
    has_social = False

    for evidence in candidate.evidence:

        if evidence.get("type") != "website_extraction":
            continue

        data = evidence.get("data", {})

        if data.get("social"):
            has_social = True
            break

    if has_social:
        score += 5
        reasons.append("social_presence")

    return {
        "score": score,
        "reasons": reasons,
    }