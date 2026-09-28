"""Coverage manifest: every text file in a GitHub repo that could change a Jevaluate verdict.

Usage: python3 coverage_manifest.py owner/repo OUTDIR
Writes OUTDIR/manifest.md, OUTDIR/meta.json and OUTDIR/files/<path with / -> __>.
Saved names never start with "." (a hidden dotfile is one nobody reads).
"""
import json, re, subprocess, sys, pathlib, urllib.request, urllib.parse

SKIP = re.compile(r"(^|/)(node_modules|vendor|dist|build|\.venv|__pycache__)/|lock|\.min\.|\.(png|jpe?g|gif|ico|webp|mp4|mov|woff2?|ttf|pdf|zip|gz|pt|bin|safetensors|onnx|pkl|npy|parquet)$", re.I)
G = {"jev": r"typesafe|system_one|systemOne|api\.typesafe\.ai|jev-[0-9]|jev-latest|\bNoul|\bChoice\b|\bScore\b",
     "decision": r"threshold|confidence|\bprob|calibrat|>=\s*0\.\d|cutoff",
     "eval": r"\blabel|\bgold\b|\beval|accuracy|brier|\bece\b|precision|recall"}
CODE_EXT = re.compile(r"\.(py|ts|tsx|js|mjs|jsx|go|rs|rb|java|kt|php|ipynb|vue|svelte|json|ya?ml|toml)$")


def saved_name(path):
    """Flatten a repo path to one file name that is never a dotfile."""
    name = path.replace("/", "__")
    return "_" + name if name.startswith(".") else name


def build_manifest(repo, out, meta, sha, tree, fetch):
    """tree: list of {'path','size'} blobs. fetch(path) -> text or None."""
    out = pathlib.Path(out); (out / "files").mkdir(parents=True, exist_ok=True)
    text = {}
    for t in tree:
        p = t["path"]
        if SKIP.search(p) or t.get("size", 0) > 200_000: continue
        try: text[p] = fetch(p)
        except Exception: text[p] = None
    hits = {p: {g: len(re.findall(r, s, re.I)) for g, r in G.items()} for p, s in text.items() if s}
    keep = {p for p, h in hits.items() if h["jev"]}
    for _ in range(2):  # follow imports of Jev-call modules
        mods = {pathlib.Path(p).stem for p in keep if pathlib.Path(p).stem not in ("__init__", "index", "README")}
        keep |= {p for p, s in text.items() if s and p not in keep and any(re.search(rf"(import|from|require\().{{0,80}}\b{re.escape(m)}\b", s) for m in mods)}
    keep |= {p for p, h in hits.items() if h["decision"] or h["eval"]} & {p for p in text if CODE_EXT.search(p)}
    keep |= {p for p in text if re.match(r"(?i)readme", pathlib.Path(p).name) and "/" not in p}
    failed = [p for p, s in text.items() if s is None]
    rows = []
    for p in sorted(keep):
        (out / "files" / saved_name(p)).write_text(text[p]); h = hits.get(p, {})
        rows.append(f"| {p} | {len(text[p])} | {h.get('jev', 0)} | {h.get('decision', 0)} | {h.get('eval', 0)} |")
    tot = sum(len(text[p]) for p in keep)
    (out / "manifest.md").write_text(
        f"# Coverage manifest: {repo} @ {sha[:10]}\n\nTree: {len(tree)} files; fetched {len(text)} text files; {len(keep)} kept ({tot} chars, ~{tot // 4} tokens). Fetch failed: {failed or 'none'}.\n"
        "Kept = Jev-call files, files importing them (2 passes), code/config with decision or eval terms, root README.\n\n"
        "| file | chars | jev | decision | eval |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
    json.dump({"repo": repo, "commit": sha, "stars": meta.get("stargazers_count"), "pushed": meta.get("pushed_at"),
               "license": (meta.get("license") or {}).get("spdx_id")}, open(out / "meta.json", "w"), indent=1)
    return {"kept": len(keep), "chars": tot}


def _gh(p): return json.loads(subprocess.run(["gh", "api", p], capture_output=True, text=True, check=True).stdout)


def main(repo, outdir):
    meta = _gh(f"repos/{repo}"); sha = _gh(f"repos/{repo}/commits/{meta['default_branch']}")["sha"]
    tree = [t for t in _gh(f"repos/{repo}/git/trees/{sha}?recursive=1")["tree"] if t["type"] == "blob"]
    fetch = lambda p: urllib.request.urlopen(urllib.request.Request(
        f"https://raw.githubusercontent.com/{repo}/{sha}/{urllib.parse.quote(p)}", headers={"User-Agent": "jevaluate"}), timeout=30).read().decode("utf-8", "ignore")
    r = build_manifest(repo, outdir, meta, sha, tree, fetch)
    print(pathlib.Path(outdir) / "manifest.md", r["kept"], "files", r["chars"], "chars")


if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
