"""Tests for library.py: run the script via subprocess against a temp JEVALUATE_LIBRARY."""
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

SCRIPT = pathlib.Path(__file__).parent / "library.py"
REAL_RATINGS_BACKUP = pathlib.Path(
    os.environ.get("JEVALUATE_REAL_BACKUP", "/nonexistent")
    
)


def run(lib_dir, *args):
    env = dict(os.environ)
    env["JEVALUATE_LIBRARY"] = str(lib_dir)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
    )


FACTS_BLOCK = "\n".join(f"- F{n} check{n} — yes. evidence:{n}" for n in range(1, 24))


def make_rating(path, project, owner, url, rated, commit="abc123def456789", verdict=4,
                 scores="execution: 3, fit: 3, coverage: 3, evidence: 2", via=None):
    via_line = f"via: {via}\n" if via else ""
    text = f"""---
project: {project}
url: {url}
owner: {owner}
rated: {rated}
rubric: 2026-09-28
commit: {commit}
depth: full
lineage: new
stages: [data-prep, question-state, execution, decision]
closes_loop: none
verdict: {verdict}
scores: {{{scores}}}
{via_line}---
## Summary
Test fixture rating for library tests.
## Facts (with evidence)
{FACTS_BLOCK}
## Verdict and reasoning
Test fixture.
"""
    path.write_text(text)
    return path


@pytest.fixture
def lib(tmp_path):
    return tmp_path / "lib"


def test_add_same_day_gives_dash2(lib, tmp_path):
    r1 = make_rating(tmp_path / "r1.md", "Proj", "owner", "https://github.com/owner/proj", "2026-09-28", commit="a" * 12)
    r2 = make_rating(tmp_path / "r2.md", "Proj", "owner", "https://github.com/owner/proj", "2026-09-28", commit="b" * 12)
    p1 = run(lib, "add", str(r1))
    assert p1.returncode == 0, p1.stdout + p1.stderr
    p2 = run(lib, "add", str(r2))
    assert p2.returncode == 0, p2.stdout + p2.stderr
    projdir = lib / "projects" / "owner__proj"
    assert (projdir / "2026-09-28.md").exists()
    assert (projdir / "2026-09-28-2.md").exists()


def test_slug_github_keeps_case(lib, tmp_path):
    r = make_rating(tmp_path / "r.md", "JevTools", "RileyCarney", "https://github.com/RileyCarney/JevTools", "2026-09-28")
    p = run(lib, "add", str(r))
    assert p.returncode == 0, p.stdout + p.stderr
    assert (lib / "projects" / "RileyCarney__JevTools" / "2026-09-28.md").exists()


def test_slug_huggingface(lib, tmp_path):
    r = make_rating(tmp_path / "r.md", "Jev-Omni", "akhilaaa3", "https://huggingface.co/akhilaaa3/Jev-Omni", "2026-09-28")
    p = run(lib, "add", str(r))
    assert p.returncode == 0, p.stdout + p.stderr
    assert (lib / "projects" / "hf__akhilaaa3__Jev-Omni" / "2026-09-28.md").exists()


def test_slug_other_site_with_path(lib, tmp_path):
    r = make_rating(tmp_path / "r.md", "AskJevs", "askjevs", "https://askjevs.site/app/play", "2026-09-28")
    p = run(lib, "add", str(r))
    assert p.returncode == 0, p.stdout + p.stderr
    assert (lib / "projects" / "site__askjevs.site__app__play" / "2026-09-28.md").exists()


def test_slug_other_site_no_path(lib, tmp_path):
    r = make_rating(tmp_path / "r.md", "AskJevs", "askjevs", "https://askjevs.site/", "2026-09-28")
    p = run(lib, "add", str(r))
    assert p.returncode == 0, p.stdout + p.stderr
    assert (lib / "projects" / "site__askjevs.site" / "2026-09-28.md").exists()


@pytest.mark.skipif(not REAL_RATINGS_BACKUP.exists(), reason="real ratings backup not present")
def test_migrate_keeps_all_19_and_orders_jevlint(lib, tmp_path):
    (lib / "ratings").mkdir(parents=True)
    for f in REAL_RATINGS_BACKUP.glob("*.md"):
        shutil.copy(f, lib / "ratings" / f.name)

    p = run(lib, "migrate")
    assert p.returncode == 0, p.stdout + p.stderr

    all_files = list(lib.glob("projects/*/*.md"))
    assert len(all_files) == 19

    index_text = (lib / "index.md").read_text()
    row_count = sum(1 for line in index_text.splitlines() if line.startswith("| 20"))
    assert row_count == 19

    assert not (lib / "ratings").exists()

    jevlint_dir = lib / "projects" / "Fox-Islam__jevlint"
    d1 = (jevlint_dir / "2026-09-27.md").read_text()
    d2 = (jevlint_dir / "2026-09-27-2.md").read_text()
    d3 = (jevlint_dir / "2026-09-27-3.md").read_text()
    orig1 = (REAL_RATINGS_BACKUP / "2026-09-27-fox-islam-jevlint.md").read_text()
    orig2 = (REAL_RATINGS_BACKUP / "2026-09-27-fox-islam-jevlint-2.md").read_text()
    orig3 = (REAL_RATINGS_BACKUP / "2026-09-27-fox-islam-jevlint-3.md").read_text()
    assert d1 == orig1
    assert d2 == orig2
    assert d3 == orig3


@pytest.mark.skipif(not REAL_RATINGS_BACKUP.exists(), reason="real ratings backup not present")
def test_migrate_is_idempotent(lib, tmp_path):
    (lib / "ratings").mkdir(parents=True)
    for f in REAL_RATINGS_BACKUP.glob("*.md"):
        shutil.copy(f, lib / "ratings" / f.name)
    run(lib, "migrate")
    p2 = run(lib, "migrate")
    assert p2.returncode == 0, p2.stdout + p2.stderr
    all_files = list(lib.glob("projects/*/*.md"))
    assert len(all_files) == 19


def test_similar_exclude_still_excludes(lib, tmp_path):
    r1 = make_rating(tmp_path / "r1.md", "ProjA", "ownera", "https://github.com/ownera/proja", "2026-09-28")
    r2 = make_rating(tmp_path / "r2.md", "ProjB", "ownerb", "https://github.com/ownerb/projb", "2026-09-28")
    run(lib, "add", str(r1))
    run(lib, "add", str(r2))
    p = run(lib, "similar", "--stage", "execution", "--exclude", "ownera/ProjA")
    assert p.returncode == 0, p.stdout + p.stderr
    assert "ownera" not in p.stdout
    assert "ProjB" in p.stdout or "ownerb" in p.stdout


def test_blind_uses_projects_layout(lib, tmp_path):
    r1 = make_rating(tmp_path / "r1.md", "ProjA", "ownera", "https://github.com/ownera/proja", "2026-09-28")
    r2 = make_rating(tmp_path / "r2.md", "ProjB", "ownerb", "https://github.com/ownerb/projb", "2026-09-28")
    run(lib, "add", str(r1))
    run(lib, "add", str(r2))
    out = tmp_path / "blind-out"
    p = run(lib, "blind", "--exclude", "ownera/proja", "--out", str(out))
    assert p.returncode == 0, p.stdout + p.stderr
    assert (out / "projects" / "ownerb__projb" / "2026-09-28.md").exists()
    assert not (out / "projects" / "ownera__proja").exists()


def test_index_ignores_evidence_folders(lib, tmp_path):
    r1 = make_rating(tmp_path / "r1.md", "ProjA", "ownera", "https://github.com/ownera/proja", "2026-09-28")
    run(lib, "add", str(r1))
    evdir = lib / "projects" / "ownera__proja" / "2026-09-28-evidence"
    evdir.mkdir(parents=True)
    (evdir / "manifest.md").write_text("# not a rating\n")
    p = run(lib, "index")
    assert p.returncode == 0, p.stdout + p.stderr
    assert "index: 1 ratings" in p.stdout


def test_list_add_writes_dated_and_latest(lib, tmp_path):
    tsv = tmp_path / "entries.tsv"
    tsv.write_text("section\turl\nSDKs\thttps://github.com/a/b\n")
    p = run(lib, "list-add", "awesome-jev", str(tsv))
    assert p.returncode == 0, p.stdout + p.stderr
    out_lines = p.stdout.strip().splitlines()
    assert len(out_lines) == 2
    dated, latest = out_lines
    assert pathlib.Path(dated).exists()
    assert pathlib.Path(latest).exists()
    assert pathlib.Path(latest).name == "entries.tsv"
    assert pathlib.Path(dated).read_text() == tsv.read_text()
