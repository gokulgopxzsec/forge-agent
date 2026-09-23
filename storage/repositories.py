import json
from datetime import datetime

from search.models import Candidate
from storage.database import get_connection


def create_research_run(task: str) -> int:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO research_runs (task, status)
        VALUES (?, ?)
        """,
        (task, "running"),
    )

    run_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return run_id


def complete_research_run(run_id: int, status: str = "completed"):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE research_runs
        SET status = ?, completed_at = ?
        WHERE id = ?
        """,
        (
            status,
            datetime.utcnow().isoformat(),
            run_id,
        ),
    )

    connection.commit()
    connection.close()


def save_candidate(candidate: Candidate, run_id: int) -> int:

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO candidates (
            run_id,
            name,
            website,
            phone,
            email,
            street,
            city,
            state,
            postcode,
            source,
            source_id,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            candidate.name,
            candidate.website,
            candidate.phone,
            None,
            candidate.street,
            candidate.city,
            candidate.state,
            candidate.postcode,
            candidate.source,
            candidate.source_id,
            candidate.status,
        ),
    )

    candidate_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return candidate_id


def save_evidence(
    candidate_id: int,
    evidence: dict,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO evidence (
            candidate_id,
            evidence_type,
            source_url,
            data
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            candidate_id,
            evidence.get("type"),
            evidence.get("url"),
            json.dumps(evidence, ensure_ascii=False),
        ),
    )

    connection.commit()
    connection.close()


def save_candidate_with_evidence(
    candidate: Candidate,
    run_id: int,
) -> int:

    candidate_id = save_candidate(
        candidate,
        run_id,
    )

    for evidence in candidate.evidence:
        save_evidence(
            candidate_id,
            evidence,
        )

    return candidate_id

def save_analysis(
    candidate_id: int,
    analysis: dict,
    model: str = "qwen3:8b",
    score: float | None = None,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO analyses (
            candidate_id,
            model,
            analysis,
            score
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            candidate_id,
            model,
            json.dumps(analysis, ensure_ascii=False),
            score,
        ),
    )

    connection.commit()
    connection.close()