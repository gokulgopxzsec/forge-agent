from search.osm import search_businesses


results = search_businesses(
    city="Houston",
    state="Texas",
    keywords=[
        "hydraulic",
        "hose",
        "fluid power"
    ],
    limit=50
)


print("=" * 70)
print("FORGE OSM DISCOVERY")
print("=" * 70)

print("Status:", results["status"])
print("Results:", results["result_count"])
print()


for index, business in enumerate(
    results["results"],
    start=1
):

    print(f"[{index}] {business['name']}")
    print("    Website:", business["website"])
    print("    Phone:", business["phone"])
    print(
        "    Address:",
        business["street"],
        business["city"],
        business["state"],
        business["postcode"]
    )
    print()