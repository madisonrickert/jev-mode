"""The Jevaluate ratings library: add a rating, rebuild the index, find similar ratings.

Location: $JEVALUATE_LIBRARY or ~/.claude/jevaluate-library/ (created on first use).
Usage:
  python3 library.py add <rating.md>          copy into projects/<slug>/ (never overwrites) and rebuild the index
  python3 library.py index                    rebuild index.md from projects/*/*.md
  python3 library.py similar [--lineage X] [--stage Y] [--limit 3] [--exclude owner/repo]
  python3 library.py check <rating.md>        check facts, fields and the verdict cap (add runs this first)
  python3 library.py blind --exclude owner/repo --out DIR
                                              copy the library without that project, for a blind re-rate
  python3 library.py migrate                  move ratings/*.md into projects/<slug>/ (idempotent)
  python3 library.py list-add <list> <entries.tsv>
                                              save a dated copy of a screened list under lists/<list>/

Layout:
  projects/<slug>/<rated>.md         one rating; a second same-day rating is <rated>-2.md, etc.
  projects/<slug>/<date>-evidence/   supporting files for a rating; never read as a rating
  lists/<name>/entries-<date>.tsv, entries.tsv (latest)
Slugs: github.com/<owner>/<repo> -> <owner>__<repo> (case kept); huggingface.co/<user>/<model> ->
hf__<user>__<model>; any other URL -> site__<domain> (no www.), plus __<path segments> if the URL has one.
"""
import os, sys, re, shutil, pathlib, argparse, datetime
from urllib.parse import urlparse

LIB = pathlib.Path(os.environ.get("JEVALUATE_LIBRARY", pathlib.Path.home() / ".claude/jevaluate-library"))
RAT = LIB / "ratings"
PROJ = LIB / "projects"

def front(p):
    t = p.read_text(errors="ignore"); m = re.match(r"---\n(.*?)\n---", t, re.S); d = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" in line:
            k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d

def slug_for(url):
    if not url:
        return "unknown"
    u = urlparse(url if "://" in url else "https://" + url)
    host = u.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    segs = [s for s in u.path.split("/") if s]
    if host == "github.com" and len(segs) >= 2:
        return f"{segs[0]}__{segs[1]}"
    if host == "huggingface.co" and len(segs) >= 2:
        return f"hf__{segs[0]}__{segs[1]}"
    slug = f"site__{host}"
    if segs:
        slug += "__" + "__".join(segs)
    return slug

def ratings_glob():
    return PROJ.glob("*/*.md")

def index():
    PROJ.mkdir(parents=True, exist_ok=True)
    rows = ["| Rated | Project | Owner | Commit | Lineage | Stages | Loop | Depth | Verdict | Via | File |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    files = sorted(ratings_glob(), key=lambda p: (front(p).get("rated", ""), str(p)), reverse=True)
    for p in files:
        d = front(p)
        via = d.get("via", "").strip() or "direct"
        rel = f"projects/{p.parent.name}/{p.name}"
        rows.append(f"| {d.get('rated','')} | {d.get('project','')} | {d.get('owner','')} | {d.get('commit','')[:10]} | {d.get('lineage','')} | {d.get('stages','')} | {d.get('closes_loop','')} | {d.get('depth','')} | {d.get('verdict','')} | {via} | {rel} |")
    (LIB / "index.md").write_text("# Jevaluate ratings\n\nNewest first. One file per rating; re-ratings are new files.\n\n" + "\n".join(rows) + "\n")
    return len(rows) - 2

def add(src):
    src = pathlib.Path(src); d = front(src)
    problems = check(src)
    if problems:
        sys.exit("not added; fix these and rerun:\n- " + "\n- ".join(problems))
    for k in ("project", "owner", "rated", "verdict"):
        if not d.get(k): sys.exit(f"missing front-matter field: {k}")
    slug = slug_for(d.get("url", ""))
    pdir = PROJ / slug; pdir.mkdir(parents=True, exist_ok=True)
    dest = pdir / f"{d['rated']}.md"
    n = 2
    while dest.exists():
        dest = pdir / f"{d['rated']}-{n}.md"; n += 1
    shutil.copy(src, dest); print(dest); print(f"index: {index()} ratings")

RUBRIC = "2026-09-28"
VALS = ("yes", "no", "n.a.", "unknown")
FACT = re.compile(r"^\s*[-*]\s*\**F(\d+)\b[^\n]*?(?:—|--|:|\*\*)\s*\**\s*(yes|no|n\.a\.|n/a|not applicable|unknown|unverified|partial|unclear)(?!\w)", re.I)

def facts(text):
    body = text.split("## Facts", 1)[-1].split("\n## ", 1)[0] if "## Facts" in text else ""
    out = {}
    for line in body.splitlines():
        m = FACT.match(line)
        if m and int(m.group(1)) not in out:
            v = m.group(2).lower()
            v = {"unclear": "invalid", "n/a": "n.a.", "not applicable": "n.a.", "unverified": "n.a."}.get(v, v)
            out[int(m.group(1))] = (v, line)
    return out

def check(src):
    p = pathlib.Path(src); t = p.read_text(errors="ignore"); d = front(p); err = []
    for k in ("project", "owner", "rated", "commit", "depth", "verdict", "scores", "rubric"):
        if not d.get(k): err.append(f"missing front-matter field: {k}")
    if d.get("rubric") and d["rubric"].split()[0] < RUBRIC: err.append(f"rubric {d['rubric']} is older than {RUBRIC}; rate with the current rubric")
    if "not recorded" in d.get("commit", ""): err.append("commit not recorded")
    v = d.get("verdict", "").split()[0] if d.get("verdict") else ""
    if v == "cant-rate": return err
    f = facts(t)
    for n in list(range(1, 24)):
        if n not in f: err.append(f"F{n} missing from ## Facts (line format: '- F{n} <name> — yes|no|n.a.|unknown. <evidence>')")
    for n, (val, line) in f.items():
        if val == "invalid": err.append(f"F{n} is 'unclear'; use yes, no, n.a. or unknown")
        if val == "partial": err.append(f"F{n} is 'partial'; use yes, no or n.a.")
        if val == "unknown" and not re.search(r"--also|fetch failed|no file", line, re.I):
            err.append(f"F{n} is unknown without a '--also' fetch noted (say 'fetch failed' or 'no file would answer it')")
    sc = dict(re.findall(r"(\w+):\s*(\d)", d.get("scores", "")))
    ex, fit, evd = (int(sc[k]) if k in sc else None for k in ("execution", "fit", "evidence"))
    no = lambda ns: [n for n in ns if f.get(n, ("",))[0] == "no"]
    core = no(list(range(1, 7)))
    if len(core) >= 2 and ex is not None and ex > 1: err.append(f"execution {ex} but {len(core)} of F1-F6 are no; anchor allows at most 1")
    elif len(core) == 1 and ex is not None and ex > 2: err.append(f"execution {ex} but F{core[0]} is no; anchor allows at most 2")
    if no([13]) and fit is not None and fit > 2: err.append("fit 3 but F13 is no; anchor allows at most 2")
    if v.isdigit():
        v = int(v); cap, why = 5, ""
        if no([6]): cap, why = 2, "F6 is no (fatal)"
        elif ex is not None and ex <= 1: cap, why = 2, f"execution {ex}"
        elif no(list(range(1, 7)) + list(range(8, 12)) + list(range(19, 23))):
            cap, why = 3, "failed " + ", ".join(f"F{n}" for n in no(list(range(1, 7)) + list(range(8, 12)) + list(range(19, 23))))
        elif evd == 0: cap, why = 3, "evidence 0"
        elif (ex or 0) < 2 or (fit or 0) < 2: cap, why = 3, "execution or fit below 2"
        if v > cap: err.append(f"verdict {v} is above the cap of {cap} ({why})")
        if v == 5 and not (ex == 3 and fit == 3 and evd == 3 and d.get("closes_loop", "none") != "none"):
            err.append("verdict 5 needs execution 3, fit 3, evidence 3 and closes_loop other than none")
    return err

def blind(exclude, out):
    out = pathlib.Path(out)
    owner, proj = exclude.lower().split("/", 1)
    hit = re.compile(re.escape(proj) + "|" + re.escape(exclude), re.I); kept = 0
    for p in ratings_glob():
        d = front(p)
        if d.get("owner", "").lower() == owner and d.get("project", "").lower() == proj: continue
        lines = ["[redacted: mentions the project under test]" if hit.search(l) and not l.startswith(("project:", "url:", "owner:")) else l
                 for l in p.read_text(errors="ignore").splitlines()]
        dest_dir = out / "projects" / p.parent.name; dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / p.name).write_text("\n".join(lines) + "\n"); kept += 1
    print(f"{kept} ratings copied to {out}, {exclude} removed and mentions redacted.")
    print(f"Rater runs with: JEVALUATE_LIBRARY={out}")

def similar(lineage, stage, limit, exclude=None):
    PROJ.mkdir(parents=True, exist_ok=True); hits = []
    for p in sorted(ratings_glob(), reverse=True):
        d = front(p); s = 0
        if exclude and f"{d.get('owner','')}/{d.get('project','')}".lower() == exclude.lower(): continue
        if lineage and lineage.split(":")[-1] in d.get("lineage", ""): s += 2
        if stage and stage in [x.strip() for x in d.get("stages", "").strip("[]").split(",")]: s += 1
        if s: hits.append((s, p, d))
    hits.sort(key=lambda h: -h[0])
    for s, p, d in hits[:limit]:
        old = "" if d.get("rubric", "") >= "2026-09-28" else "  [old rubric: context only, not precedent]"
        print(f"{p}  verdict={d.get('verdict')}  lineage={d.get('lineage')}  stages={d.get('stages')}{old}")
    if not hits: print("no similar ratings yet")

def migrate():
    if not RAT.exists() or not any(RAT.glob("*.md")):
        print("ratings/ is empty or missing; nothing to migrate")
        print(f"index: {index()} ratings")
        return
    pat = re.compile(r"^(.*?)(?:-(\d+))?\.md$")
    groups = {}
    for p in RAT.glob("*.md"):
        d = front(p)
        rated = d.get("rated", "")
        slug = slug_for(d.get("url", ""))
        m = pat.match(p.name)
        base, num = (m.group(1), int(m.group(2)) if m.group(2) else 1) if m else (p.name, 1)
        groups.setdefault((rated, slug), []).append((base, num, p))
    PROJ.mkdir(parents=True, exist_ok=True)
    moved = 0
    for (rated, slug), items in groups.items():
        items.sort(key=lambda x: (x[0], x[1]))
        pdir = PROJ / slug; pdir.mkdir(parents=True, exist_ok=True)
        for i, (base, num, p) in enumerate(items):
            name = f"{rated}.md" if i == 0 else f"{rated}-{i+1}.md"
            dest = pdir / name
            shutil.move(str(p), str(dest))
            moved += 1
    if RAT.exists() and not any(RAT.iterdir()):
        RAT.rmdir()
    print(f"migrated {moved} ratings")
    print(f"index: {index()} ratings")

def list_add(name, entries):
    entries = pathlib.Path(entries)
    today = datetime.date.today().isoformat()
    ldir = LIB / "lists" / name; ldir.mkdir(parents=True, exist_ok=True)
    dest = ldir / f"entries-{today}.tsv"
    n = 2
    while dest.exists():
        dest = ldir / f"entries-{today}-{n}.tsv"; n += 1
    shutil.copy(entries, dest)
    latest = ldir / "entries.tsv"
    shutil.copy(entries, latest)
    print(dest); print(latest)

ap = argparse.ArgumentParser()
ap.add_argument("cmd", choices=["add", "index", "similar", "check", "blind", "migrate", "list-add"])
ap.add_argument("file", nargs="?")
ap.add_argument("list_file", nargs="?")
ap.add_argument("--lineage"); ap.add_argument("--stage"); ap.add_argument("--limit", type=int, default=3); ap.add_argument("--exclude"); ap.add_argument("--out")
a = ap.parse_args()
if a.cmd == "add": add(a.file)
elif a.cmd == "check":
    problems = check(a.file); print("ok" if not problems else "- " + "\n- ".join(problems)); sys.exit(1 if problems else 0)
elif a.cmd == "blind":
    if not (a.exclude and a.out): sys.exit("blind needs --exclude owner/repo and --out DIR")
    blind(a.exclude, a.out)
elif a.cmd == "index": print(f"index: {index()} ratings")
elif a.cmd == "migrate": migrate()
elif a.cmd == "list-add":
    if not (a.file and a.list_file): sys.exit("list-add needs <list-name> <entries.tsv>")
    list_add(a.file, a.list_file)
else: similar(a.lineage, a.stage, a.limit, a.exclude)
