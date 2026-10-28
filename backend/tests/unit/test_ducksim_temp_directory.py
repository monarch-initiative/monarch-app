"""Each worker gets its own DuckDB spill directory (#1421).

DuckDB spills to `temp_directory` when a query exceeds `memory_limit`, which is correct
behaviour under load. The bug was *where* it spilled: the default is the relative path
".tmp", and spill filenames are keyed by allocation-size class rather than by process, so
every gunicorn worker resolved the same handful of paths from a shared working directory
and corrupted each other's spills.
"""

import os
from pathlib import Path

import duckdb
import pytest

from monarch_py.service.ducksim import Ducksim, worker_temp_directory


@pytest.fixture()
def temp_root(tmp_path, monkeypatch):
    monkeypatch.setenv("DUCKSIM_TEMP_ROOT", str(tmp_path / "root"))
    return tmp_path / "root"


def test_directory_is_absolute(temp_root):
    """A relative path resolves against the working directory, which every worker shares."""
    assert Path(worker_temp_directory()).is_absolute()


def test_each_call_gets_its_own_directory(temp_root):
    assert worker_temp_directory() != worker_temp_directory()


def test_directory_is_named_for_the_owning_process(temp_root):
    """The pid in the name is what lets the sweep identify directories to reclaim."""
    assert Path(worker_temp_directory()).name.startswith(f"worker-{os.getpid()}-")


def test_sweep_reclaims_directories_whose_worker_is_gone(temp_root):
    """Workers are recycled by gunicorn --max-requests, and atexit does not run on SIGKILL,
    so without a sweep the root accumulates a directory per recycled worker."""
    temp_root.mkdir(parents=True, exist_ok=True)
    dead = temp_root / "worker-999999-abandoned"
    dead.mkdir()
    (dead / "duckdb_temp_storage_S64K-0.tmp").write_bytes(b"orphaned spill")

    worker_temp_directory()

    assert not dead.exists()


def test_sweep_leaves_live_workers_alone(temp_root):
    """Sweeping a running worker's directory would cause exactly the corruption this fixes."""
    live = worker_temp_directory()
    (Path(live) / "duckdb_temp_storage_S64K-0.tmp").write_bytes(b"in use")

    worker_temp_directory()

    assert Path(live, "duckdb_temp_storage_S64K-0.tmp").exists()


def test_sweep_ignores_unrelated_directories(temp_root):
    temp_root.mkdir(parents=True, exist_ok=True)
    bystander = temp_root / "not-a-worker-dir"
    bystander.mkdir()

    worker_temp_directory()

    assert bystander.exists()


def test_from_duckdb_points_duckdb_at_the_per_worker_directory(temp_root, tmp_path):
    """The setting has to reach the connection; a spill that lands in '.tmp' is the bug."""
    source = tmp_path / "src.duckdb"
    con = duckdb.connect(str(source))
    con.execute("CREATE TABLE closure AS SELECT 'a' AS subject_id, 'rdfs:subClassOf' AS predicate_id, 'b' AS object_id")
    con.execute("CREATE TABLE information_content AS SELECT 'a' AS term, 1.0 AS ic")
    con.execute("CREATE TABLE closure_size AS SELECT 'a' AS entity, 1 AS size")
    con.close()

    sim = Ducksim.from_duckdb(source, associations=None)
    configured = sim.con.execute("SELECT current_setting('temp_directory')").fetchone()[0]

    assert Path(configured).is_absolute()
    assert Path(configured).parent == temp_root
    assert configured != ".tmp"
