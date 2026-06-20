#!/usr/bin/env python3
"""
stock-spread symbology resolver (READ-ONLY).

Maps an equity underlying (e.g. TSLA) to its per-venue identifiers across the
covered tokenized-stock venues, using an EXACT-match canonical map. Never guesses
or fuzzy/substring-matches a ticker — scam look-alike tokens exist on-chain, so a
miss returns an error rather than a guess.

Usage:
    python3 resolve.py <UNDERLYING>                 # full per-venue map for one underlying
    python3 resolve.py <UNDERLYING> --venue <venue> # a single venue's identifier
    python3 resolve.py --list                       # list known underlyings
    python3 resolve.py --selftest                   # offline fixture checks (exit 0/1)

Output: JSON to stdout. Exit 0 on success; 1 on error / unknown underlying / failed selftest.
No network. Standard library only.
"""
import json
import os
import sys

DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "symbology.json"
)


def _load():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def resolve(underlying, data=None):
    """Return the canonical per-venue record for an underlying.

    Exact match on the upper-cased key only. Raises KeyError if the underlying is
    not in the map — it never guesses or substring-matches.
    """
    data = data if data is not None else _load()
    key = underlying.strip().upper()
    underlyings = data["underlyings"]
    if key not in underlyings:
        raise KeyError(underlying)
    rec = underlyings[key]
    warnings = []
    for venue, info in rec["venues"].items():
        if info.get("id") is None:
            warnings.append(
                f"venue '{venue}' has no resolved identifier — exclude from quotes"
            )
        elif not info.get("verified", False):
            warnings.append(
                f"venue '{venue}' identifier is UNVERIFIED ({info.get('source', 'no source')}); "
                "confirm against the issuer-canonical source before trusting a live read"
            )
    return {
        "underlying": key,
        "name": rec.get("name"),
        "venues": rec["venues"],
        "warnings": warnings,
    }


def _selftest():
    data = _load()
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    # verified Solana mints resolve exactly
    check(
        "TSLA solana mint exact",
        resolve("TSLA", data)["venues"]["solana_jupiter"]["id"]
        == "XsDoVfqeBukxuZHWhdvWHBhgEHjGNst4MLodqsJHzoB",
    )
    check(
        "AAPL solana mint exact",
        resolve("AAPL", data)["venues"]["solana_jupiter"]["id"]
        == "XsbEhLAtcf6HdfpFZ5xEMdqW8nfAvcsP5bdudRLJzJp",
    )
    # case-insensitive key
    check("case-insensitive key", resolve("tsla", data) == resolve("TSLA", data))
    # unknown underlying raises (no silent guess)
    try:
        resolve("FAKE", data)
        check("unknown underlying raises", False)
    except KeyError:
        check("unknown underlying raises", True)
    # substring of a real ticker must NOT match (exact-match guard vs look-alikes)
    try:
        resolve("TSL", data)
        check("no substring match", False)
    except KeyError:
        check("no substring match", True)
    # unverified / unresolved entries surface a warning
    check(
        "NVDA unresolved solana mint warned",
        any("solana_jupiter" in w for w in resolve("NVDA", data)["warnings"]),
    )
    # schema integrity: every venue entry carries settlement + verified
    ok = True
    for _u, rec in data["underlyings"].items():
        for _v, info in rec["venues"].items():
            if "settlement" not in info or "verified" not in info:
                ok = False
    check("schema integrity (settlement+verified present)", ok)

    failed = [n for n, passed in checks if not passed]
    print(
        json.dumps(
            {
                "selftest": "PASS" if not failed else "FAIL",
                "total": len(checks),
                "passed": len(checks) - len(failed),
                "failed": failed,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--list" in argv:
        print(json.dumps(sorted(_load()["underlyings"].keys()), indent=2))
        return 0

    venue = None
    if "--venue" in argv:
        i = argv.index("--venue")
        if i + 1 < len(argv):
            venue = argv[i + 1]

    positionals = []
    skip = False
    for a in argv:
        if skip:
            skip = False
            continue
        if a == "--venue":
            skip = True
            continue
        if a.startswith("--"):
            continue
        positionals.append(a)

    if not positionals:
        print(
            json.dumps({"error": "usage: resolve.py <UNDERLYING> | --list | --selftest"}),
            file=sys.stderr,
        )
        return 1

    underlying = positionals[0]
    try:
        rec = resolve(underlying)
    except KeyError:
        print(
            json.dumps(
                {
                    "error": f"unknown underlying '{underlying}' — not in symbology map; refusing to guess"
                }
            )
        )
        return 1

    if venue:
        if venue not in rec["venues"]:
            print(json.dumps({"error": f"venue '{venue}' not covered for {rec['underlying']}"}))
            return 1
        print(json.dumps({"underlying": rec["underlying"], "venue": venue, **rec["venues"][venue]}, indent=2))
        return 0

    print(json.dumps(rec, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
