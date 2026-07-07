Ticket 4: Build the scoring engine.

For each organisation, calculate:
- metric scores where possible
- 24 assessment area/driver scores
- 12 report variable scores
- overall weighted readiness
- result band
- top repair priorities
- strengths
- 8 journey stage scores
- breakpoint stage

Result bands:
0-20 Major Barrier / Locked
21-40 Conversion Risk / Fragile
41-60 Light Friction / Emerging
61-80 Low Barrier / Functional
81-100 Strength / Strong

Hard fail:
- no report if 0 scored signals
- no report if all variables are default 50% fallback
- no report if weights do not total 100%

Add tests proving the 5 dummy organisations produce different scores/patterns.
Run tests.
