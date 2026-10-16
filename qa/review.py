"""Build the QA review page: python3 review.py <findings-dir> <out.html> [title]

Reads every <dir>/*.json (a list of findings: id, persona, title, severity bug|ux|polish,
description, proposal, optional same_as [ids]) and screenshots <dir>/<id>.png, <id>b.png, ...
Screenshots are shrunk to JPEG (macOS sips) so the page stays small.
"""
import base64, glob, html, json, os, re, shutil, subprocess, sys, tempfile

src, out = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else "QA Findings"
e = html.escape
natural = lambda i: [int(n) if n.isdigit() else n for n in re.split(r"(\d+)", i)]
items = sorted((x for f in glob.glob(f"{src}/*.json") for x in json.load(open(f))), key=lambda x: natural(x["id"]))
tmp = tempfile.mkdtemp()

def img(path):
    # ponytail: sips is macOS-only; elsewhere the full PNG is embedded
    jpg = os.path.join(tmp, os.path.basename(path) + ".jpg")
    if shutil.which("sips") and not subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "--resampleWidth", "560", path, "--out", jpg], capture_output=True).returncode:
        path, mime = jpg, "jpeg"
    else:
        mime = "png"
    return f"data:image/{mime};base64,{base64.b64encode(open(path, 'rb').read()).decode()}"

def shots(i):
    fs = sorted(glob.glob(f"{src}/{i}.png") + glob.glob(f"{src}/{i}[a-z].png"))
    return "".join(f'<button class="shot" aria-label="Enlarge screenshot"><img loading="lazy" alt="" src="{img(p)}"></button>' for p in fs)

def same(x):
    ids = x.get("same_as") or []
    return '<span class="dup">Same as ' + ", ".join(f'<a href="#{o}">{o}</a>' for o in ids) + "</span>" if ids else ""

personas = sorted({x["persona"] for x in items})
count = lambda k, v: sum(x[k] == v for x in items)
chips = "".join(f'<button class="chip" data-f="sev:{s}">{s} <b>{count("severity", s)}</b></button>' for s in ("bug", "ux", "polish")) + \
        "".join(f'<button class="chip" data-f="who:{p}">{e(p)} <b>{count("persona", p)}</b></button>' for p in personas)
cards = "".join(f'''<article id="{x["id"]}" data-sev="{x["severity"]}" data-who="{e(x["persona"])}">
  <div class="shots">{shots(x["id"])}</div>
  <div class="body">
    <div class="meta"><code>{x["id"]}</code><span class="sev {x["severity"]}">{x["severity"]}</span><span class="who">{e(x["persona"])}</span>{same(x)}</div>
    <h2>{e(x["title"])}</h2>
    <p>{e(x["description"])}</p>
    <details><summary>Proposed fix</summary><p>{e(x["proposal"])}</p></details>
  </div>
</article>''' for x in items)

open(out, "w").write(f'''<title>{e(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
/* One column of finding cards: screenshots left, words right; stacks on phones */
:root {{ --bg:#f3f5f4; --card:#fff; --fg:#17201d; --muted:#5d6b66; --line:#dbe2df; --accent:#0f7a63; --bug:#c2362b; --ux:#b86e00; --polish:#4b62b3;
  --display:"Bricolage Grotesque",system-ui,sans-serif; --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,monospace }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f1513; --card:#18201d; --fg:#e6ece9; --muted:#93a39d; --line:#2a3531; --accent:#3cc4a2; --bug:#ff7a6e; --ux:#f0a640; --polish:#8ea2ff; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#0f1513; --card:#18201d; --fg:#e6ece9; --muted:#93a39d; --line:#2a3531; --accent:#3cc4a2; --bug:#ff7a6e; --ux:#f0a640; --polish:#8ea2ff; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.55 var(--sans); padding-block:32px 64px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)) }}
main {{ max-width:980px; margin:0 auto; display:grid; gap:20px }}
h1 {{ font:700 clamp(28px,5vw,40px)/1.1 var(--display); margin:0; text-wrap:balance }}
.lede {{ color:var(--muted); margin:6px 0 0 }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px }}
.chip {{ font:500 13px var(--sans); color:var(--fg); background:var(--card); border:1px solid var(--line); border-radius:99px; padding:6px 12px; cursor:pointer; text-transform:capitalize }}
.chip b {{ color:var(--muted); font-weight:500; margin-left:4px }}
.chip[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent); color:var(--bg) }}
.chip[aria-pressed="true"] b {{ color:inherit }}
.chip:focus-visible, .shot:focus-visible, summary:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px }}
article {{ display:grid; grid-template-columns:minmax(0,220px) minmax(0,1fr); gap:20px; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; scroll-margin-top:16px }}
article:target {{ border-color:var(--accent) }}
.shots {{ display:grid; gap:8px; align-content:start }}
.shot {{ padding:0; border:1px solid var(--line); border-radius:10px; overflow:hidden; cursor:zoom-in; background:none; display:block }}
.shot img {{ display:block; width:100%; height:auto }}
.body {{ min-width:0 }}
.meta {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; font-size:13px; color:var(--muted) }}
code {{ font:500 12px var(--mono); color:var(--muted) }}
.sev {{ font:500 11px var(--mono); text-transform:uppercase; letter-spacing:.06em; padding:2px 8px; border-radius:99px; border:1px solid currentColor }}
.sev.bug {{ color:var(--bug) }} .sev.ux {{ color:var(--ux) }} .sev.polish {{ color:var(--polish) }}
.dup a {{ color:var(--accent) }}
.who {{ text-transform:capitalize }}
h2 {{ font:600 20px/1.25 var(--display); margin:8px 0 6px; text-wrap:balance }}
.body p {{ margin:0 0 10px; max-width:65ch }}
details {{ border-top:1px solid var(--line); padding-top:8px }}
summary {{ cursor:pointer; font-weight:500; color:var(--accent) }}
details p {{ margin-top:8px; color:var(--muted) }}
dialog {{ border:none; padding:0; background:none; max-width:min(92vw,520px) }}
dialog::backdrop {{ background:rgba(0,0,0,.75) }}
dialog img {{ width:100%; border-radius:12px; display:block }}
@media (max-width:640px) {{ article {{ grid-template-columns:minmax(0,1fr) }} .shots {{ grid-template-columns:repeat(auto-fill,minmax(120px,1fr)) }} }}
</style>
<main>
  <header><h1>{e(title)}</h1><p class="lede">{len(items)} issues from {len(personas)} fake users. Tap a screenshot to enlarge it.</p></header>
  <div class="chips">{chips}</div>
  {cards}
</main>
<dialog id="zoom"><img alt="Screenshot, enlarged"></dialog>
<script>
const zoom = document.getElementById("zoom");
document.addEventListener("click", (ev) => {{
  const s = ev.target.closest(".shot");
  if (s) {{ zoom.querySelector("img").src = s.querySelector("img").src; zoom.showModal(); return; }}
  if (ev.target.closest("dialog")) {{ zoom.close(); return; }}
  const c = ev.target.closest(".chip");
  if (!c) return;
  const on = c.getAttribute("aria-pressed") !== "true";
  document.querySelectorAll(".chip").forEach((x) => x.setAttribute("aria-pressed", "false"));
  c.setAttribute("aria-pressed", String(on));
  const [k, v] = c.dataset.f.split(":");
  document.querySelectorAll("article").forEach((a) => (a.hidden = on && a.dataset[k] !== v));
}});
</script>
''')
shutil.rmtree(tmp)
print(f"{len(items)} findings -> {out} ({os.path.getsize(out) // 1024} KB)")
