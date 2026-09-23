from search.osm import search_businesses
from search.normalize import normalize_osm
from search.dedupe import deduplicate_candidates
from search.enrich import enrich_candidate

from storage.database import initialize_database
from storage.repositories import (
    create_research_run,
    complete_research_run,
    save_candidate_with_evidence,
    save_analysis,
)

from ai.qualify import qualify_candidate
from ai.scoring import calculate_lead_score


def run_research(
    task: str,
    city: str,
    state: str,
    keywords: list[str],
):

    print()
    print("=" * 70)
    print("FORGE AGENT")
    print("LOCAL AI RESEARCH ENGINE")
    print("=" * 70)

    print()
    print("TASK")
    print("-" * 70)
    print(task)

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------

    initialize_database()

    run_id = create_research_run(task)

    try:

        # -----------------------------------------------------
        # 1. DISCOVERY
        # -----------------------------------------------------

        print()
        print("[1/7] Discovering businesses...")
        print("-" * 70)

        discovery = search_businesses(
            city=city,
            state=state,
            keywords=keywords,
        )

        if discovery.get("status") != "ok":

            complete_research_run(
                run_id,
                status="failed",
            )

            print("Discovery failed.")
            return

        print(
            f"Discovered: "
            f"{discovery.get('result_count', 0)}"
        )

        # -----------------------------------------------------
        # 2. NORMALIZE
        # -----------------------------------------------------

        print()
        print("[2/7] Normalizing candidates...")
        print("-" * 70)

        candidates = normalize_osm(
            discovery["results"]
        )

        print("Candidates:", len(candidates))

        # -----------------------------------------------------
        # 3. DEDUPLICATE
        # -----------------------------------------------------

        print()
        print("[3/7] Deduplicating...")
        print("-" * 70)

        candidates = deduplicate_candidates(
            candidates
        )

        print("Unique candidates:", len(candidates))

        # -----------------------------------------------------
        # 4. WEBSITE + EXTRACTION
        # -----------------------------------------------------

        print()
        print("[4/7] Resolving and extracting websites...")
        print("-" * 70)

        enriched_candidates = []

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            print()
            print(
                f"[{index}/{len(candidates)}] "
                f"{candidate.name}"
            )

            try:

                candidate = enrich_candidate(
                    candidate
                )

                enriched_candidates.append(
                    candidate
                )

            except Exception as e:

                print(
                    "Enrichment error:",
                    repr(e),
                )

                candidate.status = (
                    "enrichment_failed"
                )

                enriched_candidates.append(
                    candidate
                )

        # -----------------------------------------------------
        # 5. SAVE CANDIDATES
        # -----------------------------------------------------

        print()
        print("[5/7] Saving research evidence...")
        print("-" * 70)

        saved = []

        for candidate in enriched_candidates:

            candidate_id = (
                save_candidate_with_evidence(
                    candidate,
                    run_id,
                )
            )

            saved.append(
                (
                    candidate,
                    candidate_id,
                )
            )

        print(
            "Saved candidates:",
            len(saved),
        )

        # -----------------------------------------------------
        # 6. QWEN ANALYSIS
        # -----------------------------------------------------

        print()
        print("[6/7] Qwen3 qualification...")
        print("-" * 70)

        for candidate, candidate_id in saved:

            if not candidate.website:
                print(
                    f"Skipping {candidate.name}: "
                    "no website"
                )
                continue

            if not candidate.evidence:
                print(
                    f"Skipping {candidate.name}: "
                    "no evidence"
                )
                continue

            print()
            print(
                "Analyzing:",
                candidate.name,
            )

            try:

                analysis = qualify_candidate(
                    candidate
                )

                scoring = calculate_lead_score(
                    candidate,
                    analysis,
                )

                score = scoring["score"]

                save_analysis(
                    candidate_id=candidate_id,
                    analysis={
                        **analysis,
                        "score_reasons": (
                            scoring["reasons"]
                        ),
                    },
                    model="qwen3:8b",
                    score=score,
                )

                print(
                    "Score:",
                    score,
                    "/ 100",
                )

            except Exception as e:

                print(
                    "AI analysis failed:",
                    repr(e),
                )

        # -----------------------------------------------------
        # 7. COMPLETE
        # -----------------------------------------------------

        complete_research_run(
            run_id,
            status="completed",
        )

        print()
        print("=" * 70)
        print("RESEARCH COMPLETE")
        print("=" * 70)

        print()
        print("Research Run:", run_id)
        print(
            "Candidates:",
            len(saved),
        )

    except Exception as e:

        complete_research_run(
            run_id,
            status="failed",
        )

        print()
        print("=" * 70)
        print("RESEARCH FAILED")
        print("=" * 70)

        print()
        print(repr(e))


if __name__ == "__main__":

    run_research(
        task=(
            "Find hydraulic hose businesses "
            "in Houston"
        ),

        city="Houston",
        state="Texas",

        keywords=[
            "hydraulic",
            "hose",
            "fluid power",
        ],
    )