import re
from urllib.parse import urlparse

from search.models import Candidate


def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    value = value.lower().strip()

    # Remove punctuation
    value = re.sub(r"[^a-z0-9]+", " ", value)

    # Normalize whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""

    return re.sub(r"\D", "", phone)


def normalize_email(email: str | None) -> str:
    if not email:
        return ""

    return email.lower().strip()


def normalize_domain(url: str | None) -> str:
    if not url:
        return ""

    try:
        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]

        return domain
    except Exception:
        return ""


def candidate_keys(candidate: Candidate) -> set[str]:
    keys = set()

    # Company name
    name = normalize_text(candidate.name)

    if name:
        location = normalize_text(candidate.city)

        if location:
            keys.add(f"name:{name}|city:{location}")
        else:
            keys.add(f"name:{name}")

    # Website
    domain = normalize_domain(candidate.website)

    if domain:
        keys.add(f"domain:{domain}")

    # Phone
    phone = normalize_phone(candidate.phone)

    if phone:
        keys.add(f"phone:{phone}")

    return keys


def deduplicate_candidates(
    candidates: list[Candidate],
) -> list[Candidate]:

    unique: list[Candidate] = []
    seen: dict[str, Candidate] = {}

    for candidate in candidates:

        keys = candidate_keys(candidate)

        duplicate = None

        for key in keys:
            if key in seen:
                duplicate = seen[key]
                break

        if duplicate:
            # Merge useful information
            if not duplicate.website and candidate.website:
                duplicate.website = candidate.website

            if not duplicate.phone and candidate.phone:
                duplicate.phone = candidate.phone

            if not duplicate.street and candidate.street:
                duplicate.street = candidate.street

            if not duplicate.postcode and candidate.postcode:
                duplicate.postcode = candidate.postcode

            duplicate.evidence.extend(candidate.evidence)

            continue

        unique.append(candidate)

        for key in keys:
            seen[key] = candidate

    return unique