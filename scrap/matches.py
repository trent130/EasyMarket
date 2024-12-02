from pt import fetch_data

print(fetch_data)

for sport in data["data"]:
    for category in sport["categories"]:
        for competition in category["competitions"]:
            if "matches" in competition:  # Check if matches exist
                for match in competition["matches"]:
                    print(f"Match details: {match}")
