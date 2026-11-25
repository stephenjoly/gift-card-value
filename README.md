# Gift card value checker

A single-page, no-backend tool that answers one question: **what are my reward points actually worth when
I redeem them for gift cards?**

It takes one catalogue snapshot (82 e-gift cards, with the points each denomination costs) and turns it
into a filterable comparison, so you can rule out the shops you never use and see what's left.

Live: <https://gift-cards.stephenjoly.net>

## How the numbers work

| Term | Meaning |
|---|---|
| Points per $1 | Points needed per $1 of gift-card face value. Lower is better. |
| Cash back at 5× | `100 × 5 ÷ points per $1` — the return on a purchase made in a 5× category. |
| Cash back at 1× | `100 × 1 ÷ points per $1` — the same purchase on a 1× category. |
| Vs. 1¢/point | `100 ÷ points per $1 × 100` — how the redemption compares with a 1 cent per point baseline. |

The page assumes the common baseline of **100 points ≈ $1**. If your redemption rate differs, every
percentage shifts by the same ratio, so the ranking does not change.

## Layout

```
build.py        Rebuilds site/cards.js from data/cards.csv (adds categories, recomputes the math)
data/cards.csv  Store, face value, points, points per $1  (one snapshot)
site/index.html The whole page: markup, styles, filters, sorting, the rate ruler
site/cards.js   Generated — never edit by hand
Dockerfile      nginx:alpine serving site/ with a /healthz probe
nginx.conf      Static server config
```

## Update the data

1. Replace `data/cards.csv` with a fresh catalogue export (same four columns).
2. If a store is new, add it to `CATEGORY` in `build.py`.
3. Run `python3 build.py`.
4. Commit, and the deployment picks it up.

## Local preview

```bash
python3 build.py
cd site && python3 -m http.server 8099
```

## Privacy

No analytics, no cookies beyond nothing at all, no accounts, no network calls from the browser. The page is
one HTML file, one generated JS file and an inline SVG icon.

## Disclaimer

Unofficial. Not affiliated with MBNA, its rewards programme or any retailer named. Figures come from a
single catalogue snapshot (November 2026) and are for comparison only — not financial advice. Verify current
point prices in your own rewards portal before redeeming.
