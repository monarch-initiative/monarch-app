"""Rewrite the KG schema in a canonical order, and report whether it changed meaning.

The published schema's slot order is not stable between KG builds: 2026-09-02 and
2026-09-04 declare identical slots in a different sequence. Committing it verbatim
turns that into a ~300-line pull request with no content in it, which then has to be
read to establish that it says nothing.

Canonicalizing on the way in makes ordering carry no information, so anything left in a
diff is a real change. Identity fields keep their position at the front because slot
order reaches users as column order in the CLI's table and TSV output -- a plain
alphabetical sort would lead `Entity` with `broad_synonym` and bury `id`.

Needs `linkml_runtime` for validation, which the backend environment provides.

Usage:
    canonicalize_kg_schema.py FETCHED.yaml COMMITTED.yaml
        Writes the canonical form of FETCHED to COMMITTED.
        Exit 0 if COMMITTED changed meaning, 1 if it did not (or did not exist),
        2 if FETCHED is not a valid LinkML schema.
"""

import sys
from pathlib import Path

import yaml

# Slots that lead a class, in this order, when the class has them. Everything else is
# sorted alphabetically after these.
LEAD_SLOTS = [
    "id",
    "category",
    "subject",
    "predicate",
    "object",
    "name",
    "full_name",
    "symbol",
    "description",
]

# Mappings whose key order is presentation, not meaning.
SORTED_MAPPINGS = ("prefixes", "slots", "classes")


def order_slots(slots):
    """Identity slots first in LEAD_SLOTS order, then the rest alphabetically."""
    lead = [slot for slot in LEAD_SLOTS if slot in slots]
    return lead + sorted(slot for slot in slots if slot not in lead)


def canonicalize(doc):
    """Return `doc` with every ordering decision made the same way every time."""
    result = {}
    for key in sorted(doc):
        value = doc[key]
        if key in SORTED_MAPPINGS and isinstance(value, dict):
            value = {name: value[name] for name in sorted(value)}
            if key == "classes":
                value = {
                    name: {
                        **{k: body[k] for k in sorted(body) if k != "slots"},
                        **({"slots": order_slots(body["slots"])} if "slots" in body else {}),
                    }
                    for name, body in value.items()
                }
        result[key] = value
    return result


def validate(path: Path) -> None:
    """Fail unless the file parses as a LinkML schema, not merely as YAML.

    `SchemaView` builds a `SchemaDefinition`, so this rejects a 404 page, a stray
    list, and a document that is valid YAML but carries keys the metamodel does not
    define -- none of which a "does it have a `classes` key" check would catch.

    Imported here rather than at module scope so the import cost, and the dependency,
    belong to the one function that needs them. It comes from `linkml_runtime`, not
    the `linkml` codegen package: oaklib depends on it directly, so it stays available
    even if `linkml` is ever demoted to a dev-only dependency.
    """
    from linkml_runtime.utils.schemaview import SchemaView

    SchemaView(str(path)).all_classes()


def main(fetched: Path, committed: Path) -> int:
    try:
        validate(fetched)
    except ImportError:
        print(
            "linkml_runtime is required to validate the fetched schema; run this with the backend environment",
            file=sys.stderr,
        )
        return 2
    except Exception as err:
        print(f"{fetched} is not a valid LinkML schema: {err}", file=sys.stderr)
        return 2

    doc = yaml.safe_load(fetched.read_text())

    # Compare canonical forms, not raw ones. Slot lists compare order-sensitively, so
    # comparing as-fetched would report a change for exactly the reordering this is
    # meant to absorb. Canonicalizing both sides is also what lets this catch a
    # reordering that canonicalize() does not yet normalize: the two forms still differ
    # only if something other than ordering moved.
    canonical = canonicalize(doc)
    previous = yaml.safe_load(committed.read_text()) if committed.exists() else None
    committed.write_text(yaml.safe_dump(canonical, sort_keys=False, default_flow_style=False, width=100))
    if previous is not None and canonicalize(previous) == canonical:
        print("Schema is unchanged in meaning; nothing to regenerate.")
        return 1
    print("Schema changed; regenerating the model.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
