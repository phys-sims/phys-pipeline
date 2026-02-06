#!/usr/bin/env python3
import argparse
import datetime as dt
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ADR_DIR = os.path.join(ROOT, "docs", "adr")
INDEX = os.path.join(ADR_DIR, "INDEX.md")

# Matches:
#   0001-some-title.md
#   ECO-0001-some-title.md
RE_NUMERIC = re.compile(r"^(?P<num>[0-9]{4})-(?P<slug>.+)\.md$")
RE_PREFIXED = re.compile(r"^(?P<prefix>[A-Z]{2,8})-(?P<num>[0-9]{4})-(?P<slug>.+)\.md$")


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def iter_adr_files(series: str):
    """
    series:
      - "numeric"  -> only 0001-*.md
      - "all"      -> both numeric and prefixed
      - "ECO"/...  -> only <SERIES>-0001-*.md (exact prefix match)
    """
    os.makedirs(ADR_DIR, exist_ok=True)

    for p in glob.glob(os.path.join(ADR_DIR, "*.md")):
        base = os.path.basename(p)

        # skip templates + index
        if base.startswith("_template-"):
            continue
        if base.upper() == "INDEX.MD":
            continue

        m_num = RE_NUMERIC.match(base)
        m_pre = RE_PREFIXED.match(base)

        if series == "numeric":
            if m_num:
                yield p, None, int(m_num.group("num"))
        elif series == "all":
            if m_num:
                yield p, None, int(m_num.group("num"))
            elif m_pre:
                yield p, m_pre.group("prefix"), int(m_pre.group("num"))
        else:
            # series treated as an exact prefix like "ECO" / "INT"
            if m_pre and m_pre.group("prefix") == series:
                yield p, m_pre.group("prefix"), int(m_pre.group("num"))


def next_id(series: str) -> str:
    ids = []
    for _p, _prefix, n in iter_adr_files(series):
        ids.append(n)
    return f"{(max(ids) + 1 if ids else 1):04d}"


def read_front_matter(path):
    meta = {}
    with open(path, encoding="utf-8") as f:
        s = f.read()
    if s.startswith("---"):
        parts = s.split("\n---", 1)
        if len(parts) > 1:
            fm = parts[0].lstrip("-\n")
            for line in fm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    allowed_keys = {"title", "status", "date", "area", "tags", "impacted_repos"}
    md_kv = re.compile(r"^\s*(?:[-*]\s*)?\*\*(.+?):\*\*\s*(.+?)\s*$")
    for line in s.splitlines():
        m = md_kv.match(line)
        if not m:
            continue
        key = m.group(1).strip().lower()
        if key not in allowed_keys:
            continue
        value = m.group(2).strip().strip("`")
        meta.setdefault(key, value)

    # fallback: first markdown H1 as title
    if "title" not in meta:
        m = re.search(r"^#\s+(.+)$", s, flags=re.M)
        if m:
            meta["title"] = m.group(1).strip()
    return meta


def cmd_new(args):
    os.makedirs(ADR_DIR, exist_ok=True)

    tid = next_id(args.series)
    slug = slugify(args.title)

    # file naming
    if args.series == "numeric":
        base = f"{tid}-{slug}.md"
        adr_label_prefix = "ADR"
    elif args.series == "all":
        sys.exit(
            "Refusing to create ADR with --series all. Use --series numeric or a prefix like ECO."
        )
    else:
        base = f"{args.series}-{tid}-{slug}.md"
        adr_label_prefix = args.series

    fname = os.path.join(ADR_DIR, base)

    tmpl = {
        "full": "_template-full.md",
        "lite": "_template-lite.md",
        "amend": "_template-amend.md",
    }[args.type]
    src = os.path.join(ADR_DIR, tmpl)
    if not os.path.exists(src):
        sys.exit(f"Template not found: {src}")

    with open(src, encoding="utf-8") as f:
        s = f.read()

    # Backwards compatible: existing templates only need <ADR-ID> and <DATE>.
    # If you add <ADR-PREFIX> to templates, it will be filled too.
    s = (
        s.replace("<ADR-ID>", tid)
        .replace("<ADR-PREFIX>", adr_label_prefix)
        .replace("<DATE>", dt.date.today().isoformat())
    )

    with open(fname, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

    print(f"Created {os.path.relpath(fname, ROOT)}")


def cmd_reindex(args):
    rows = []

    for p, prefix, n in sorted(iter_adr_files(args.series), key=lambda t: ((t[1] or "ADR"), t[2])):
        base = os.path.basename(p)
        meta = read_front_matter(p)

        title = meta.get("title", base)
        status = meta.get("status", "")
        date = meta.get("date", "")
        area = meta.get("area", "")
        tags = meta.get("tags", "")

        # Optional: if you add "impacted_repos:" to front matter in ECO ADRs
        impacted = meta.get("impacted_repos", "")

        link = base

        label = f"{prefix}-{n:04d}" if prefix else f"ADR-{n:04d}"
        ref = f"[{label}]({link})"

        # If series is a single prefix (e.g., ECO), include impacted column;
        # otherwise keep old shape.
        if args.series not in ("numeric", "all"):
            rows.append((label, ref, title, status, date, area, impacted, tags))
        else:
            rows.append((label, ref, title, status, date, area, tags))

    if args.series not in ("numeric", "all"):
        lines = [
            f"# {args.series} ADR Index",
            "",
            "| ADR | Title | Status | Date | Area | Impacted repos | Tags |",
            "|---:|---|---|---|---|---|---|",
        ]
        for _label, ref, t, s, d, ar, imp, tg in rows:
            lines.append(f"| {ref} | {t} | {s} | {d} | {ar} | {imp} | {tg} |")
    else:
        lines = [
            "# ADR Index",
            "",
            "| ADR | Title | Status | Date | Area | Tags |",
            "|---:|---|---|---|---|---|",
        ]
        for _label, ref, t, s, d, ar, tg in rows:
            lines.append(f"| {ref} | {t} | {s} | {d} | {ar} | {tg} |")

    os.makedirs(ADR_DIR, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Updated {os.path.relpath(INDEX, ROOT)} with {len(rows)} ADRs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    pnew = sub.add_parser("new")
    pnew.add_argument("title")
    pnew.add_argument("--type", choices=["full", "lite", "amend"], default="full")
    pnew.add_argument(
        "--series",
        default="numeric",
        help=(
            'Which ADR series to use: "numeric" (0001-*), "ECO" (ECO-0001-*), '
            '"INT", or "all" (index only).'
        ),
    )
    pnew.set_defaults(func=cmd_new)

    pre = sub.add_parser("reindex")
    pre.add_argument(
        "--series",
        default="numeric",
        help='Which ADR series to index: "numeric", "ECO", "INT", or "all".',
    )
    pre.set_defaults(func=cmd_reindex)

    args = ap.parse_args()
    args.func(args)
