#!/usr/bin/env python3
"""Build the gift-card dataset (site/cards.js) from data/cards.csv.

Source: an MBNA Rewards e-gift-card catalogue snapshot (Nov 2026).
Each row: Store, Face value, Points, Points per $1, 5x cashback %, 1x cashback %.
We add a spending category to every store and recompute the percentages so the
page never depends on hand-typed numbers.
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "data" / "cards.csv"
OUT = ROOT / "site" / "cards.js"

# One category per store. Categories describe *what you spend on*, so a visitor
# can switch off the kinds of spending they never do.
CATEGORY = {
    "LEGO": "Toys & gaming",
    "Roblox": "Toys & gaming",
    "Nintendo eShop": "Toys & gaming",
    "Microsoft Xbox": "Toys & gaming",
    "PlayStation Store": "Toys & gaming",
    "Sephora": "Beauty",
    "Bath & Body Works": "Beauty",
    "Petsmart": "Pets",
    "One4all Ultimate Choice": "Multi-store",
    "GAP OPTIONS": "Fashion",
    "TJX (Winners, Homesense & Marshalls)": "Fashion",
    "lululemon": "Fashion",
    "American Eagle Outfitters": "Fashion",
    "H&M": "Fashion",
    "Reitmans": "Fashion",
    "The Ultimate Dining": "Dining",
    "The Keg Steakhouse + Bar\u00ae": "Dining",
    "Earls": "Dining",
    "Subway": "Dining",
    "Tim Hortons": "Coffee & snacks",
    "Starbucks": "Coffee & snacks",
    "Dollarama": "Everyday",
    "Walmart": "Everyday",  # groceries + household, so it sits with everyday spend
    "Airbnb": "Travel",
    "Esso": "Gas & auto",
    "Cineplex": "Movies",
    "Best Buy": "Electronics",
    "DoorDash": "Delivery & rides",
    "Uber & Uber Eats": "Delivery & rides",
    "Bass Pro Shops": "Outdoors",
    "Home Depot": "Home & hardware",
    "Amazon": "Online",
    "Indigo": "Books & hobbies",
    "Kobo": "Books & hobbies",
}

# Plain-language note per category, used for the filter tooltips / blurbs.
CATEGORY_NOTE = {
    "Toys & gaming": "Toys, consoles, game stores and kids' brands.",
    "Beauty": "Makeup, skincare and bath products.",
    "Pets": "Pet food, supplies and grooming.",
    "Multi-store": "Usable at many different retailers, not one shop.",
    "Fashion": "Clothing, shoes and accessories.",
    "Dining": "Restaurants and fast food.",
    "Coffee & snacks": "Coffee shops and quick treats.",
    "Everyday": "Groceries, household and variety-store runs.",
    "Travel": "Stays and trips.",
    "Gas & auto": "Fuel and vehicle spending.",
    "Movies": "Cinema tickets and concessions.",
    "Home & hardware": "Renovation, tools, garden and building supplies.",
    "Electronics": "Tech, appliances and gadgets.",
    "Delivery & rides": "Food delivery and rideshare.",
    "Outdoors": "Camping, fishing and outdoor gear.",
    "Online": "Online marketplace shopping.",
    "Books & hobbies": "Books, ebooks and reading.",
}

# Display order on the page: most broadly useful first.
ORDER = [
    "Everyday", "Dining", "Coffee & snacks", "Fashion", "Beauty",
    "Toys & gaming", "Electronics", "Home & hardware", "Books & hobbies", "Movies",
    "Travel", "Gas & auto", "Delivery & rides", "Outdoors", "Pets",
    "Online", "Multi-store",
]


def main() -> None:
    rows = []
    with SRC.open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            store = raw["Store"].strip()
            face = int(raw["Face value"])
            points = int(raw["Points"])
            ppd = round(points / face, 2)
            category = CATEGORY.get(store)
            if category is None:
                raise SystemExit(f"Uncategorised store: {store!r}")
            rows.append({
                "store": store,
                # Short label for the table; the full name stays in `store`.
                "label": store.split(" (")[0],
                "face": face,
                "points": points,
                "ppd": ppd,
                "cat": category,
                # Value of the redemption relative to 1 cent per point.
                "value": round(10000 / ppd, 1),
                "cb5": round(500 / ppd, 2),
                "cb1": round(100 / ppd, 2),
            })

    rows.sort(key=lambda r: (r["ppd"], r["store"]))
    for i, row in enumerate(rows, 1):
        row["rank"] = i

    cats = []
    for name in ORDER:
        items = [r for r in rows if r["cat"] == name]
        if not items:
            continue
        best = items[0]
        cats.append({
            "name": name,
            "note": CATEGORY_NOTE[name],
            "stores": sorted({r["label"] for r in items}),
            "best": best["store"],
            "bestValue": best["value"],
            "bestFace": best["face"],
        })

    meta = {
        "cards": len(rows),
        "stores": len({r["store"] for r in rows}),
        "categories": len(cats),
        "bestPpd": rows[0]["ppd"],
        "worstPpd": rows[-1]["ppd"],
        "bestValue": rows[0]["value"],
        "worstValue": rows[-1]["value"],
        "bestCb5": rows[0]["cb5"],
        "worstCb5": rows[-1]["cb5"],
        "bestStore": rows[0]["store"],
        "bestFace": rows[0]["face"],
        "worstStore": rows[-1]["store"],
        "worstFace": rows[-1]["face"],
        "snapshot": "November 2026",
    }

    payload = (
        "// Generated by build.py — edit data/cards.csv instead.\n"
        f"window.GC = {{meta: {json.dumps(meta, ensure_ascii=False)},\n"
        f"categories: {json.dumps(cats, ensure_ascii=False)},\n"
        f"cards: {json.dumps(rows, ensure_ascii=False)}}};\n"
    )
    OUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT} — {len(rows)} cards, {len(cats)} categories, "
          f"ppd {meta['bestPpd']}..{meta['worstPpd']}")


if __name__ == "__main__":
    main()
