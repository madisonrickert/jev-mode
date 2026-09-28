"""Tests for coverage_manifest.py, screen_list.py and jev_callsites.py.
Network tests are opt-in: JEV_NETWORK=1 pytest test_scripts.py"""
import json, os, pathlib, subprocess, sys
import pytest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
NET = pytest.mark.skipif(not os.environ.get("JEV_NETWORK"), reason="set JEV_NETWORK=1 for network tests")


# ---------- coverage_manifest ----------
def test_saved_name_never_starts_with_dot(tmp_path):
    import coverage_manifest as cm
    tree = [{"path": ".github/workflows/ci.yml", "type": "blob", "size": 40},
            {"path": "src/client.py", "type": "blob", "size": 40}]
    files = {".github/workflows/ci.yml": "name: ci\nenv: TYPESAFE_API_KEY\n",
             "src/client.py": "import typesafe\n"}
    cm.build_manifest("o/r", tmp_path, {"stargazers_count": 1, "pushed_at": "x"}, "a" * 40, tree, files.get)
    saved = sorted(p.name for p in (tmp_path / "files").iterdir())
    assert saved and not any(n.startswith(".") for n in saved), saved
    assert any("github__workflows__ci.yml" in n for n in saved)
    manifest = (tmp_path / "manifest.md").read_text()
    assert ".github/workflows/ci.yml" in manifest  # manifest still shows the true path


# ---------- screen_list ----------
README = """# Awesome Jev

## Contents
- [Official](#official)

## Official
- [Docs](https://docs.typesafe.ai/introduction) - API docs.

## Applications
- [One](https://github.com/a/one) - first app
- [Two](https://github.com/b/two.git) - second
- [One again](https://github.com/A/One) - duplicate of one
- [Blog](https://example.com/post) - not github

## Agent Tools
- [Three](https://github.com/c/three) - tool

## Contribute
- [Rules](https://github.com/x/y) - ignored
"""


def test_parser_counts_sections_and_dedupes():
    import screen_list as sl
    rows, counts = sl.parse_readme(README)
    assert counts == {"Official": 1, "Applications": 3, "Agent Tools": 1}
    assert [r["repo"] for r in rows if r["section"] == "Applications"] == ["a/one", "b/two", ""]


def test_strict_pattern_ignores_prose_from_typesafe():
    import screen_list as sl
    assert not sl.strict_hit("Built with Jev, a model\nfrom\nTypeSafe that answers questions.\n")
    assert sl.strict_hit("import os\nfrom typesafe import Client\n")
    assert sl.strict_hit("client = Typesafe::Client.new\n")
    assert sl.strict_hit('url = "https://api.typesafe.ai/v1/x"')


def test_classify_uses_tree_and_raw_files_not_code_search():
    import screen_list as sl
    tree = ["README.md", "lib/typesafe/sdk.rb", "notes.txt"]
    raw = {"lib/typesafe/sdk.rb": "module Typesafe\n  Client = Typesafe::Client\nend\n", "README.md": "from\nTypeSafe"}
    cls, ev = sl.classify(tree, raw.get)
    assert cls == "hosted call" and "lib/typesafe/sdk.rb" in ev
    raw["app.py"] = "print('hi')\nfrom\nTypeSafe\n"
    cls, _ = sl.classify(["README.md", "app.py"], raw.get)
    assert cls == "no hosted call found"


def test_known_yes_no_check_aborts_when_pattern_wrong():
    import screen_list as sl
    yes_tree, no_tree = ["a.py"], ["b.py"]
    trees = {"y/y": (yes_tree, {"a.py": "from typesafe import X"}), "n/n": (no_tree, {"b.py": "from\nTypeSafe"})}
    load = lambda repo: (trees[repo][0], trees[repo][1].get)
    sl.check_known("y/y", "n/n", load)  # passes
    trees["n/n"] = (no_tree, {"b.py": "import typesafe"})
    with pytest.raises(SystemExit) as e:
        sl.check_known("y/y", "n/n", load)
    assert "known-no" in str(e.value)
    trees["n/n"] = (no_tree, {"b.py": "x"}); trees["y/y"] = (yes_tree, {"a.py": "x"})
    with pytest.raises(SystemExit) as e:
        sl.check_known("y/y", "n/n", load)
    assert "known-yes" in str(e.value)


def test_cli_refuses_without_known_flags(tmp_path):
    readme = tmp_path / "r.md"; readme.write_text(README)
    r = subprocess.run([sys.executable, str(HERE / "screen_list.py"), str(readme)], capture_output=True, text=True)
    assert r.returncode != 0 and "--known-yes" in r.stderr and "--known-no" in r.stderr
    r = subprocess.run([sys.executable, str(HERE / "screen_list.py"), str(readme), "--known-yes", "a/b"], capture_output=True, text=True)
    assert r.returncode != 0 and "--known-no" in r.stderr


def test_cli_dry_run_prints_parser_counts(tmp_path):
    readme = tmp_path / "r.md"; readme.write_text(README)
    r = subprocess.run([sys.executable, str(HERE / "screen_list.py"), str(readme), "--known-yes", "a/b", "--known-no", "c/d", "--counts-only"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "Applications: 3" in r.stdout and "total: 5" in r.stdout, r.stdout + r.stderr


# ---------- jev_callsites ----------
def callsites(path):
    r = subprocess.run([sys.executable, str(HERE / "jev_callsites.py"), str(path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.JSONDecoder().raw_decode(r.stdout)[0]


def make_tree(root, files):
    for rel, text in files.items():
        p = pathlib.Path(root) / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    return root


def test_imitation_adapter_docs_and_fixtures_are_mentions_not_hosted_calls(tmp_path):
    make_tree(tmp_path, {
        "src/adapter.py": "# serves the System One API locally\ndef system_one(questions):\n    return Noul('x')\n# route: /v1/systemone\n",
        "src/metrics.py": "from jevmlx.evalmetrics import typesafe_agreement\n",
        "tests/test_api.py": "URL = 'https://api.typesafe.ai/v1/systemone'\nsystem_one(1)\n",
        "test_top.py": "URL = 'https://api.typesafe.ai'\n",
        "docs/api.py": "URL = 'https://api.typesafe.ai'\n",
        "fixtures/resp.yaml": "url: https://api.typesafe.ai\n",
        "examples/data.json": '{"url": "https://api.typesafe.ai"}',
        "README.md": "Calls api.typesafe.ai and typesafe/jev-1.13.0\n"})
    out = callsites(tmp_path)
    assert out["hosted_calls"] == 0
    assert out["mentions"] > 0 and "call_sites" not in out


@pytest.mark.parametrize("name,text", [
    ("lib/typesafe/sdk.rb", 'DEFAULT_BASE_URL = "https://api.typesafe.ai"\n'),
    ("src/client.py", 'DEFAULT_MODEL = "~typesafe/jev-latest"\n'),
    ("app/main.py", "import os\nfrom typesafe import Client\n"),
    ("app/main2.py", "import typesafe_ai\n"),
    ("web/index.ts", "import { TypeSafe } from '@typesafe-ai/sdk'\n"),
    ("scripts/run.sh", "curl --model typesafe/jev-1.13 x\n"),
    ("lib/app.rb", "client = Typesafe::SDK::Client.new(api_key: k)\n"),
])
def test_endpoint_sdk_or_gateway_id_counts_as_hosted_call(tmp_path, name, text):
    make_tree(tmp_path, {name: text})
    assert callsites(tmp_path)["hosted_calls"] > 0


def test_json_data_files_do_not_count_as_hosted_calls(tmp_path):
    make_tree(tmp_path, {"analysis/run.json": '{"served_model": "typesafe/jev-1.13-20260917"}'})
    assert callsites(tmp_path)["hosted_calls"] == 0


@NET
@pytest.mark.parametrize("repo,expect_zero", [("bnsd55/jevmlx", True), ("joshmn/typesafe-sdk", False), ("chepyle/jev-test", False)])
def test_real_repos_hosted_calls(tmp_path, repo, expect_zero):
    subprocess.run(["gh", "repo", "clone", repo, str(tmp_path / "r"), "--", "--depth", "1", "-q"], check=True)
    out = callsites(tmp_path / "r")
    assert (out["hosted_calls"] == 0) == expect_zero, out


@NET
def test_real_known_yes_known_no_screen():
    import screen_list as sl
    sl.check_known("joshmn/typesafe-sdk", "bnsd55/jevmlx", sl.load_repo)
