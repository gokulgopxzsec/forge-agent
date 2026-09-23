from search.website import discover_website


TEST_COMPANIES = [
    {
        "name": "OneHydraulics",
        "city": "Houston",
        "state": "Texas",
    },
    {
        "name": "Hose Master",
        "city": "Houston",
        "state": "Texas",
    },
]


def print_result(result):
    print("Status:", result.get("status"))
    print("Method:", result.get("method"))

    best = result.get("best")

    if best:
        print()
        print("BEST CANDIDATE")
        print("-" * 60)
        print("URL:", best.get("url"))
        print("Domain:", best.get("domain"))
        print("Title:", best.get("title"))
        print("Score:", best.get("score"))
        print("Evidence:", best.get("evidence"))
        print("Matched:", best.get("matched_tokens"))

    direct = result.get("direct_candidates", [])

    if direct:
        print()
        print("DIRECT DOMAIN CANDIDATES")
        print("-" * 60)

        for i, candidate in enumerate(direct, 1):
            print(
                f"[{i}] "
                f"{candidate.get('domain')} "
                f"| score={candidate.get('score')} "
                f"| {candidate.get('title')}"
            )

    search = result.get("search_candidates", [])

    if search:
        print()
        print("SEARCH CANDIDATES")
        print("-" * 60)

        for i, candidate in enumerate(search, 1):
            print(
                f"[{i}] "
                f"{candidate.get('url')} "
                f"| relevance={candidate.get('relevance_score'):.1f}"
            )

    print()


if __name__ == "__main__":

    for company in TEST_COMPANIES:

        print("=" * 70)
        print(
            f"WEBSITE DISCOVERY: "
            f"{company['name']}"
        )
        print("=" * 70)
        print()

        result = discover_website(
            company_name=company["name"],
            city=company["city"],
            state=company["state"],
        )

        print_result(result)