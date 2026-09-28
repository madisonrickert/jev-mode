"""Count Jev usage in a folder or file: mentions, hosted calls, question types, thresholds, model pinning, confidence use.

`mentions` counts every textual hit (system_one(, api.typesafe.ai, /v1/systemone), docs and tests included.
`hosted_calls` counts only real reach-outs to hosted Jev: the endpoint (api.typesafe.ai), an SDK client
construction or import, or a gateway model ID (typesafe/jev...), in code or config files outside tests/, test_*,
docs/, fixtures/, examples/ data files and *.md; .json data files (results, analysis) never count. An adapter
that imitates the API, or docs and fixtures, gives mentions but hosted_calls 0.

Usage: python3 jev_callsites.py <path> [--list]
Pattern counts are a starting point: confirm them against the code you read.
"""
import re, sys, pathlib, json

EXT = {".py", ".ts", ".tsx", ".js", ".mjs", ".rb", ".go", ".rs", ".java", ".kt", ".php", ".md", ".json", ".yaml", ".yml", ".toml", ".sh"}
PAT = {
    "mentions": r"system_one\s*\(|systemOne\s*\(|api\.typesafe\.ai|/v1/systemone",
    "noul": r"\bNoul\s*\(|[\"']?type[\"']?\s*:\s*[\"']noul[\"']",
    "choice": r"\bChoice\s*\(|[\"']?type[\"']?\s*:\s*[\"']choice[\"']",
    "score": r"\bScore\s*\(|[\"']?type[\"']?\s*:\s*[\"']score[\"']",
    "confidence_used": r"\.confidence\b|\.probabilities\b|\.noul\s*[<>]=?",
    "model_pinned": r"jev-\d+\.\d+\.\d+",
    "model_alias": r"jev-(latest|preview)\b|jev-\d+\.\d+(?![.\d])",
    "threshold_consts": r"^\s*[A-Z][A-Z0-9_]*(THRESH|CUTOFF|FLOOR|MIN|MAX|CONF|_T)\w*\s*[:=]\s*0?\.\d+",
    "threshold_in_prose": r"\b(above|below|over|under|at least|greater than|less than)\s+0?\.\d+\b",
}
HOSTED = re.compile(
    r"api\.typesafe\.ai|@typesafe-ai/sdk|^[ \t]*from[ \t]+typesafe(_ai|_sdk)?[ \t]+import|^[ \t]*import[ \t]+typesafe(_ai|_sdk)?\b"
    r"|require\(?[ \t]*['\"]typesafe|Typesafe::(SDK::)?Client|typesafe/jev[\w.\-]*", re.I | re.M)
NOT_HOSTED_DIRS = {"tests", "test", "spec", "docs", "fixtures"}
DATA_EXT = {".json", ".yaml", ".yml", ".toml"}
HOSTED_EXT = EXT - {".md", ".json"}


def counts_as_hosted_file(f: pathlib.Path, root: pathlib.Path) -> bool:
    rel = f.relative_to(root) if root.is_dir() else pathlib.Path(f.name)
    if any(part in NOT_HOSTED_DIRS for part in rel.parts[:-1]): return False
    if f.name.startswith("test_") or f.stem.endswith("_test"): return False
    if f.suffix in DATA_EXT and "examples" in rel.parts[:-1]: return False
    return f.suffix in HOSTED_EXT or f.name == "package.json"


KEEP = ("typesafe", "system_one", "systemone", "noul", "jev")

def files(root: pathlib.Path):
    if root.is_file():
        yield root; return
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in EXT and not any(x in p.parts for x in (".git", "node_modules", ".venv", "venv", "dist")):
            yield p

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); sys.exit(0 if len(sys.argv) > 1 else 2)
    root = pathlib.Path(sys.argv[1]); show = "--list" in sys.argv
    if not root.exists():
        sys.exit(f"path not found: {root}")
    tot = {k: 0 for k in PAT}; where = {k: [] for k in PAT}; jev_files = []; hosted = 0; hosted_where = []
    for f in files(root):
        try: text = f.read_text(errors="ignore")
        except Exception: continue
        if not any(k in text.lower() for k in KEEP): continue
        jev_files.append(str(f))
        if counts_as_hosted_file(f, root):
            n = len(HOSTED.findall(text))
            hosted += n
            if n and len(hosted_where) < 8: hosted_where.append(f.name)
        for i, line in enumerate(text.splitlines(), 1):
            for k, rx in PAT.items():
                n = len(re.findall(rx, line, re.I if k != "threshold_consts" else 0))
                if n:
                    tot[k] += n
                    if show and len(where[k]) < 8: where[k].append(f"{f.name}:{i}")
    q = tot["noul"] + tot["choice"] + tot["score"]
    out = {"files_mentioning_jev": len(jev_files), "mentions": tot["mentions"], "hosted_calls": hosted,
           **{k: v for k, v in tot.items() if k != "mentions"}, "questions_total": q,
           "questions_per_hosted_call": round(q / hosted, 1) if hosted else None}
    print(json.dumps(out, indent=2))
    if show:
        print(json.dumps({k: v for k, v in where.items() if v} | ({"hosted_calls": hosted_where} if hosted_where else {}), indent=2))
    print("NOTE: question counts are static. A question built inside a loop or comprehension counts once; read the code for runtime counts.")
    if hosted == 0:
        print("NOTE: hosted_calls is 0" + (f" ({tot['mentions']} mentions are docs, tests, fixtures or an imitation of the API)" if tot["mentions"] else "") + ". Check for wrappers or MCP tools before rating 'Jev in name only'.")

if __name__ == "__main__":
    main()
