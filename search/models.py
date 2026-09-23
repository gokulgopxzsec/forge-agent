from dataclasses import dataclass, field


@dataclass
class Candidate:
    name: str

    website: str | None = None
    phone: str | None = None

    street: str | None = None
    city: str | None = None
    state: str | None = None
    postcode: str | None = None

    source: str | None = None
    source_id: str | None = None

    evidence: list[dict] = field(default_factory=list)

    status: str = "discovered"