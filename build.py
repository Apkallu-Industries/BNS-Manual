"""Build the BNS parts / panel pages that the direct-part-marking QR codes point at (static GitHub Pages site).

Every QR on a BNS part encodes <base>/<airframe>/parts/<P/N> or <base>/<airframe>/panels/<code>. This script scans the
marking tables for those addresses and writes one page per address at the same path, so when the shared QR base is
switched from the placeholder (manual.blacknet.example) to this site, every existing mark resolves without changing
anything else.

Published per part (catalogue fields only): P/N, name, nomenclature, category, lifecycle, dash numbers, where-used,
Four Horsemen programme. Provenance and source references are NEVER published (they can name subscription sources).

    python build.py --register <part_number_register.json> --scan <dir-or-file> [--scan ...] --out site
"""
import argparse, collections, html, json, re, shutil
from pathlib import Path

PLACEHOLDER = "https://manual.blacknet.example"
URL_RE = re.compile(re.escape(PLACEHOLDER) + r"(/[A-Za-z0-9_\-/]+)")
AIRFRAMES = {"b2": "B-2 Spirit (BNS)", "b3": "B-3 / B3-A Spirit (BNS)"}
CSS = """:root{--bg:#f4f4f1;--fg:#16181a;--mut:#5d6266;--card:#fff;--line:#d9dbd6;--acc:#4a5a2a}
@media (prefers-color-scheme:dark){:root{--bg:#121413;--fg:#e8e9e6;--mut:#9aa09b;--card:#1b1e1c;--line:#2c312d;--acc:#a8bb6e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:760px;margin:0 auto;padding:24px 16px 48px}a{color:var(--acc)}h1{font-size:1.5rem;margin:.2em 0}
.k{color:var(--mut);font-size:.85rem;text-transform:uppercase;letter-spacing:.06em}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:14px 0}
table{width:100%;border-collapse:collapse}td{padding:6px 4px;border-top:1px solid var(--line);vertical-align:top}td:first-child{color:var(--mut);width:34%}
code{font-family:ui-monospace,Consolas,monospace}.pn{font-family:ui-monospace,Consolas,monospace;font-size:1.1rem}
ul{padding-left:1.2em}input{width:100%;padding:10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font-size:1rem}
footer{color:var(--mut);font-size:.8rem;margin-top:32px}"""


def page(title, body, depth):
    up = "../" * depth
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)}</title><link rel=stylesheet href='{up}style.css'></head><body><main>"
            f"<p class=k><a href='{up}'>BlackNet Systems parts and panels</a></p>{body}"
            "<footer>BlackNet Systems. Fighting in the Name of Peace. Catalogue data for the BNS DCS World programme; "
            "fictional manufacturer. Generated from the BNS parts register.</footer></main></body></html>")


def usage(u):
    if isinstance(u, dict):
        return f"{u.get('aircraft', '?')}, qty {u.get('qty', '?')}" + (f", dash {', '.join(u['dashes'])}" if u.get("dashes") else "")
    return str(u)


def rows(pairs):
    return "<table>" + "".join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in pairs if v) + "</table>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", required=True)
    ap.add_argument("--scan", action="append", default=[])
    ap.add_argument("--out", default="site")
    a = ap.parse_args()
    reg = {e["pn"]: e for e in json.loads(Path(a.register).read_text(encoding="utf-8"))}
    paths = set()
    for s in a.scan:
        p = Path(s)
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.suffix in (".json", ".lua", ".py") and ".git" not in f.parts]
        for f in files:
            try:
                paths.update(URL_RE.findall(f.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                pass
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "style.css").write_text(CSS, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    index = collections.defaultdict(list)
    for path in sorted(paths):
        parts = path.strip("/").split("/")
        if len(parts) != 3 or parts[1] not in ("parts", "panels"):
            continue
        af, kind, key = parts
        e = reg.get(key) if kind == "parts" else None
        if kind == "parts":
            title = e["name"] if e else key
            body = f"<h1>{html.escape(title)}</h1><p class=pn>{html.escape(key)}</p>"
            if e:
                dash = "".join(f"<li><code>{html.escape(k)}</code> {html.escape(v)}</li>" for k, v in e.get("dash_numbers", {}).items())
                used = "".join(f"<li>{html.escape(usage(u))}</li>" for u in e.get("used_on", []))
                prog = e.get("programme")
                body += "<div class=card>" + rows([
                    ("Nomenclature", html.escape(e.get("nomenclature", ""))), ("Category", html.escape(e.get("category", ""))),
                    ("ATA chapter", html.escape(e.get("ata", ""))), ("Status", html.escape(e.get("lifecycle", ""))),
                    ("Dash numbers", f"<ul>{dash}</ul>" if dash else ""), ("Where used", f"<ul>{used}</ul>" if used else ""),
                    ("Programme", html.escape(f"{prog['name']}: {prog['rider']}") if prog else "")]) + "</div>"
            else:
                body += "<div class=card><p>This part carries a BNS mark; its catalogue entry is not published yet.</p></div>"
        else:
            title = f"Panel {key}"
            body = f"<h1>Panel {html.escape(key)}</h1><div class=card><p>Crew-manual page for panel <code>{html.escape(key)}</code> on the {html.escape(AIRFRAMES.get(af, af))}. Panel content is not published yet.</p></div>"
        body += f"<p><a href='../'>All {html.escape(AIRFRAMES.get(af, af))} {kind}</a></p>"
        d = out / af / kind / key
        d.mkdir(parents=True)
        (d / "index.html").write_text(page(title, body, 3), encoding="utf-8")
        index[(af, kind)].append((key, title))
    for (af, kind), items in index.items():
        li = "".join(f"<li><a href='{html.escape(k)}/'><code>{html.escape(k)}</code></a> {html.escape(t) if t != k else ''}</li>" for k, t in items)
        (out / af / kind / "index.html").write_text(page(f"{AIRFRAMES.get(af, af)} {kind}", f"<h1>{html.escape(AIRFRAMES.get(af, af))}: {kind}</h1><ul>{li}</ul>", 2), encoding="utf-8")
        for p in ((out / af / "index.html"),):
            secs = "".join(f"<li><a href='{k}/'>{k}</a></li>" for (x, k) in index if x == af)
            p.write_text(page(AIRFRAMES.get(af, af), f"<h1>{html.escape(AIRFRAMES.get(af, af))}</h1><ul>{secs}</ul>", 1), encoding="utf-8")
    total = sum(len(v) for v in index.values())
    secs = "".join(f"<li><a href='{af}/{kind}/'>{html.escape(AIRFRAMES.get(af, af))}: {kind}</a> ({len(v)})</li>" for (af, kind), v in sorted(index.items()))
    (out / "index.html").write_text(page("BlackNet Systems parts and panels",
        f"<h1>BlackNet Systems parts and panels</h1><p>The pages behind the QR marks on BNS parts. Scan a part's QR, or browse:</p><ul>{secs}</ul>", 0), encoding="utf-8")
    (out / "404.html").write_text(page("Not found", "<h1>Not found</h1><p>No BNS page at this address.</p>", 0).replace("href=''", "href='/BNS-Manual/'").replace("href='style.css'", "href='/BNS-Manual/style.css'"), encoding="utf-8")
    print(f"{total} pages from {len(paths)} QR addresses")


if __name__ == "__main__":
    main()
