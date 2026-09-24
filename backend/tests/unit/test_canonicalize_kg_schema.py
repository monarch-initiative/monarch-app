"""Tests for the KG schema canonicalizer.

The point of the script is that a reshuffled-but-equivalent schema produces no diff and
no pull request, while a real change still does. Both halves are worth pinning: getting
the first wrong brings the noise back, getting the second wrong means a schema change
lands silently without regenerating the model.
"""

import importlib.util
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "canonicalize_kg_schema.py"
spec = importlib.util.spec_from_file_location("canonicalize_kg_schema", SCRIPT)
canon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canon)


def schema(entity_slots, association_slots=("id", "subject"), name_range="string"):
    return {
        "name": "monarch-kg",
        "id": "https://monarch/kg",
        "prefixes": {"biolink": "b", "dct": "d"},
        "slots": {"name": {"range": name_range}, "id": {"range": "uriorcurie"}},
        "classes": {
            "Entity": {"description": "an entity", "slots": list(entity_slots)},
            "Association": {"description": "an edge", "slots": list(association_slots)},
        },
    }


def write(tmp_path, doc, name):
    path = tmp_path / name
    path.write_text(yaml.safe_dump(doc, sort_keys=False))
    return path


def test_reordering_is_not_a_change(tmp_path):
    """The case this exists for: 2026-09-02 and 2026-09-04 declared identical slots in
    a different order, which produced a ~300-line pull request with nothing in it."""
    committed = write(tmp_path, schema(["id", "name", "category"]), "committed.yaml")
    canon.main(write(tmp_path, schema(["id", "name", "category"]), "a.yaml"), committed)
    reordered = write(tmp_path, schema(["category", "name", "id"]), "b.yaml")
    assert canon.main(reordered, committed) == 1


def test_added_slot_is_a_change(tmp_path):
    committed = write(tmp_path, schema(["id", "name"]), "committed.yaml")
    canon.main(write(tmp_path, schema(["id", "name"]), "a.yaml"), committed)
    assert canon.main(write(tmp_path, schema(["id", "name", "extra"]), "b.yaml"), committed) == 0


def test_changed_range_is_a_change(tmp_path):
    """A reordering-only comparison would miss this, since no slot moved."""
    committed = write(tmp_path, schema(["id", "name"]), "committed.yaml")
    canon.main(write(tmp_path, schema(["id", "name"]), "a.yaml"), committed)
    changed = write(tmp_path, schema(["id", "name"], name_range="uriorcurie"), "b.yaml")
    assert canon.main(changed, committed) == 0


def test_output_is_stable_across_orderings(tmp_path):
    """Two equivalent inputs must produce byte-identical files, or the diff comes back."""
    one, two = tmp_path / "one.yaml", tmp_path / "two.yaml"
    canon.main(write(tmp_path, schema(["id", "name", "category"]), "a.yaml"), one)
    canon.main(write(tmp_path, schema(["category", "id", "name"]), "b.yaml"), two)
    assert one.read_text() == two.read_text()


def test_identity_slots_lead_their_class(tmp_path):
    """Slot order reaches users as CLI table and TSV column order, so a plain
    alphabetical sort would lead Entity with `broad_synonym` and bury `id`."""
    out = tmp_path / "out.yaml"
    canon.main(write(tmp_path, schema(["zebra", "broad_synonym", "name", "id", "category"]), "a.yaml"), out)
    slots = yaml.safe_load(out.read_text())["classes"]["Entity"]["slots"]
    assert slots == ["id", "category", "name", "broad_synonym", "zebra"]


def test_association_leads_with_its_own_identity_slots(tmp_path):
    out = tmp_path / "out.yaml"
    doc = schema(["id"], association_slots=["agent_type", "object", "subject", "predicate", "id"])
    canon.main(write(tmp_path, doc, "a.yaml"), out)
    slots = yaml.safe_load(out.read_text())["classes"]["Association"]["slots"]
    assert slots[:4] == ["id", "subject", "predicate", "object"]


def test_missing_committed_file_counts_as_a_change(tmp_path):
    """First run has nothing to compare against, so it must regenerate rather than
    silently skip."""
    out = tmp_path / "absent.yaml"
    assert canon.main(write(tmp_path, schema(["id"]), "a.yaml"), out) == 0
    assert out.exists()


@pytest.mark.parametrize("content", ["<html>404</html>", "", "- just\n- a\n- list\n"])
def test_non_schema_input_is_rejected(tmp_path, content):
    """A 404 page written over the schema would otherwise regenerate the model from
    nothing."""
    bad = tmp_path / "bad.yaml"
    bad.write_text(content)
    committed = write(tmp_path, schema(["id"]), "committed.yaml")
    before = committed.read_text()
    assert canon.main(bad, committed) == 2
    assert committed.read_text() == before, "a rejected fetch must not overwrite the schema"
