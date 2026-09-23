from search.osm import search_businesses
from search.normalize import normalize_osm


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


candidates = normalize_osm(
    results["results"]
)


print("=" * 70)
print("FORGE DISCOVERY PIPELINE")
print("=" * 70)

print()
print("Discovered:", len(candidates))
print()


for index, candidate in enumerate(
    candidates,
    start=1
):

    print(f"[{index}] {candidate.name}")

    print("    Status:", candidate.status)
    print("    Source:", candidate.source)
    print("    Source ID:", candidate.source_id)
    print("    Website:", candidate.website)
    print("    Phone:", candidate.phone)
    print()