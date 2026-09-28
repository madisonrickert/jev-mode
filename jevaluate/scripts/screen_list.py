"""Screen every GitHub entry of an awesome-list README for a real hosted-Jev call.

Usage: python3 screen_list.py README.md --known-yes owner/repo --known-no owner/repo [--out screen.tsv] [--counts-only]

A real hosted call = api.typesafe.ai, a TypeSafe SDK import, a TYPESAFE key, or a gateway model ID.
Classification fetches each repo's tree (gh api) and greps raw files (raw.githubusercontent.com).
It never uses GitHub code search: that index missed joshmn/typesafe-sdk, whose tree has lib/typesafe/sdk.rb.
The known-yes and known-no repos are classified first; the run aborts if either is wrong
(e.g. a loose "from typesafe" once matched the prose "from\\nTypeSafe" in bnsd55/jevmlx).
Section counts come from this script's own parser; do not trust a hand count.
"""
import argparse, csv, json, re, subprocess, sys, urllib.parse, urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# Import forms are line-anchored (re.M) so prose spanning lines cannot match.
STRICT = re.compile(
    r"api\.typesafe\.ai|@typesafe-ai/sdk|['\"]typesafe-ai['\"]"
    r"|^[ \t]*from[ \t]+typesafe(_ai)?[ \t]+import|^[ \t]*import[ \t]+typesafe(_ai)?\b"
    r"|require\(['\"]typesafe|typesafe[-_]sdk|Typesafe::|TYPESAFE_API_KEY|TYPESAFE_KEY"
    r"|typesafe-ai/(typesafe-sdk|system-one)|typesafe/jev|typesafe-ai/jev|openrouter[^\n]{0,80}jev",
    re.I | re.M)
CODE = re.compile(r"\.(py|ts|tsx|js|mjs|cjs|jsx|go|rs|rb|java|kt|swift|php|cs|ex|exs|ipynb|vue|svelte|sh|toml|json|ya?ml|gemspec|env\.example)$|(^|/)(Gemfile|Cargo\.toml|package\.json|\.env\.example)$", re.I)
SKIP = re.compile(r"(^|/)(node_modules|vendor|dist|build|\.venv)/|lock|\.min\.", re.I)
PRIORITY = re.compile(r"package\.json|pyproject|requirements|Gemfile|Cargo|go\.mod|client|api|sdk|jev|typesafe", re.I)
MAX_FILES = 250


def strict_hit(text):
    m = STRICT.search(text)
    return m.group(0) if m else None


def parse_readme(text):
    """-> (rows, counts). Rows are unique entries (by repo, else URL) outside Contents/Contribute/License."""
    sec, rows, seen = None, [], set()
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m: sec = m.group(1).strip(); continue
        m = re.match(r"^\s*[-*]\s+\[([^\]]+)\]\(([^)]+)\)\s*[-–:]?\s*(.*)", line)
        if not m or sec in (None, "Contents", "Contribute", "License"): continue
        name, url, desc = m.groups(); url = url.strip()
        g = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", url)
        repo = (g.group(1) + "/" + g.group(2)).removesuffix(".git") if g else ""
        key = repo.lower() or url
        if key in seen: continue
        seen.add(key)
        desc = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", desc).replace("\t", " ").strip()[:160]
        rows.append({"section": sec, "name": name, "url": url, "repo": repo, "description": desc})
    return rows, dict(Counter(r["section"] for r in rows))


def classify(paths, raw):
    """paths: blob paths of a repo tree; raw(path) -> text (or None/raises). -> (cls, evidence)."""
    code = [p for p in paths if CODE.search(p) and not SKIP.search(p)]
    code.sort(key=lambda p: (0 if PRIORITY.search(p) else 1, len(p)))
    checked = 0
    for p in code[:MAX_FILES]:
        try: s = raw(p)
        except Exception: continue
        if s is None: continue
        checked += 1
        hit = strict_hit(s)
        if hit: return "hosted call", f"{p} ({hit})"
    if not code: return "no code", ""
    if not checked: return "fetch failed", ""
    return "no hosted call found" + (" (partial)" if len(code) > MAX_FILES else ""), ""


def _gh(p): return json.loads(subprocess.run(["gh", "api", p], capture_output=True, text=True, check=True).stdout)


def load_repo(repo):
    """-> (blob paths, raw fetcher) from the default branch tree; no code search."""
    meta = _gh(f"repos/{repo}"); sha = _gh(f"repos/{repo}/commits/{meta['default_branch']}")["sha"]
    tree = _gh(f"repos/{repo}/git/trees/{sha}?recursive=1")
    paths = [t["path"] for t in tree["tree"] if t["type"] == "blob" and t.get("size", 0) < 300_000]
    raw = lambda p: urllib.request.urlopen(urllib.request.Request(
        f"https://raw.githubusercontent.com/{repo}/{sha}/{urllib.parse.quote(p)}", headers={"User-Agent": "jevaluate"}), timeout=20).read().decode("utf-8", "ignore")
    return paths, raw


def check_known(known_yes, known_no, load):
    """Run the pattern on both control repos first; abort if either comes out wrong."""
    for label, repo, want in (("known-yes", known_yes, "hosted call"), ("known-no", known_no, "no hosted call found")):
        cls, ev = classify(*load(repo))
        print(f"{label} {repo}: {cls}" + (f" [{ev}]" if ev else ""))
        if not cls.startswith(want):
            sys.exit(f"ABORT: {label} {repo} classified {cls!r}, expected {want!r}. The pattern is wrong; nothing screened.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("readme"); ap.add_argument("--out", default="screen.tsv")
    ap.add_argument("--known-yes", required=True, metavar="OWNER/REPO", help="repo that certainly makes a hosted call (e.g. joshmn/typesafe-sdk)")
    ap.add_argument("--known-no", required=True, metavar="OWNER/REPO", help="repo that certainly does not (e.g. bnsd55/jevmlx)")
    ap.add_argument("--counts-only", action="store_true", help="print parser counts and stop (no network)")
    a = ap.parse_args()
    rows, counts = parse_readme(open(a.readme).read())
    for s, n in counts.items(): print(f"{s}: {n}")
    print(f"total: {len(rows)}; github: {sum(1 for r in rows if r['repo'])}")
    if a.counts_only: return
    check_known(a.known_yes, a.known_no, load_repo)

    def one(r):
        r.update(cls="not screened", evidence="")
        if r["repo"]:
            try: r["cls"], r["evidence"] = classify(*load_repo(r["repo"]))
            except Exception as e: r.update(cls="fetch failed", evidence=str(e)[:100])
        return r
    with ThreadPoolExecutor(8) as ex: out = list(ex.map(one, rows))
    with open(a.out, "w") as fh:
        w = csv.DictWriter(fh, list(out[0].keys()), delimiter="\t"); w.writeheader(); w.writerows(out)
    c = Counter((r["section"], r["cls"]) for r in out)
    for (s, k), v in sorted(c.items()): print(f"{s} | {k}: {v}")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
