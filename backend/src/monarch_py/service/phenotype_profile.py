"""Ranking for collapsed phenotype rows (see dismech_store.DismechStore.phenotype_profile).

A row is one phenotype of a disease (or one disease of a phenotype) collapsed across the KG's
primary knowledge sources, with any dismech records that corroborate it.
"""

import math

# lower edge of each HPO frequency band; Excluded (HP:0040285) scores as unknown
FREQUENCY_BAND_FLOOR = {
    "HP:0040280": 1.0,
    "HP:0040281": 0.8,
    "HP:0040282": 0.3,
    "HP:0040283": 0.05,
    "HP:0040284": 0.01,
}
# coarse tiers on the consensus score; source count breaks ties within a tier
FREQUENCY_TIERS = (0.5, 0.2, 0.05)


def wilson_lower_bound(count: int, total: int, z: float = 1.96) -> float:
    """95% lower bound on a proportion, so 1/1 ranks below 700/1827"""
    if total <= 0:
        return 0.0
    p = count / total
    centre = p + z * z / (2 * total)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return max(0.0, (centre - margin) / (1 + z * z / total))


def frequency_score(row: dict) -> float | None:
    """mean frequency estimate across a row's KG sources, so disagreeing sources pull it down.

    dismech's frequency is a fallback only, used when no KG source gives one, so AI-assisted
    curation never outranks OMIM/Orphanet.
    """
    scores = []
    for o in row["observations"]:
        if o.get("count") is not None and o.get("total"):
            scores.append(wilson_lower_bound(o["count"], o["total"]))
        elif o.get("percentage") is not None:
            scores.append(o["percentage"] / 100)
        elif o.get("frequency") in FREQUENCY_BAND_FLOOR:
            scores.append(FREQUENCY_BAND_FLOOR[o["frequency"]])
    if not scores:
        scores = [
            FREQUENCY_BAND_FLOOR[m["frequency_hp"]]
            for m in row["dismech"]
            if m.get("frequency_hp") in FREQUENCY_BAND_FLOOR
        ]
    return sum(scores) / len(scores) if scores else None


def rank_key(row: dict) -> tuple:
    """negated last; diagnostic first; then frequency tier, KG source count, dismech
    corroboration, score, label. dismech breaks ties only after KG sources, like frequency."""
    score = row["frequency_score"]
    tier = len(FREQUENCY_TIERS) + 1 if score is None else sum(score < t for t in FREQUENCY_TIERS)
    return (
        row["negated"],
        not any(m["diagnostic"] for m in row["dismech"]),
        tier,
        -len(row["sources"]),
        not row["dismech"],
        -(score or 0),
        (row["label"] or "").lower(),
    )
