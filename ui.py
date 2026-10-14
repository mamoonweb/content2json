#!/usr/bin/env python3
"""
ui.py - Simple local web UI for content_to_json.

    pip install python-docx
    python ui.py            # opens http://127.0.0.1:8765

Upload one or many .docx files + the Elementor template .json, review the auto-suggested mapping
(edit it with dropdowns), click Generate, download JSON / report / mapping config.
Everything runs locally; nothing is uploaded anywhere.
"""
import argparse
import base64
import io
import json
import re
import threading
import traceback
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import content_to_json as core

SESSIONS = {}
GROUP_TYPES = ("call-to-action", "image-box", "button")


# values derivable from a document title such as "Albert Services -- Clayton Electrical Web Page"
VAR_DEFS = {
    "page_name": {"label": "Page name", "regex": r"--\s*(.+?)\s+Web Page\s*$"},
    "last_word": {"label": "Page name, last word", "regex": r"(\w+)\s+Web Page\s*$"},
    "first_word": {"label": "Page name, first word", "regex": r"--\s*(\w+)"},
}


def derive_vars(doc):
    out = {}
    for k, d in VAR_DEFS.items():
        m = re.search(d["regex"], doc.title or "")
        if m:
            out[k] = m.group(1).strip()
    return out


# ----------------------------------------------------------------------------
# analysis helpers
# ----------------------------------------------------------------------------
def doc_summary(doc):
    secs = []
    for s in doc.sections:
        secs.append({
            "index": s.index,
            "title": s.title.text if s.title else None,
            "counts": {"paras": len(s.intro), "cards": len(s.cards), "buttons": len(s.buttons),
                       "items": len(s.items), "placeholders": len(s.placeholders)},
            "nodes": [{"kind": n.kind, "level": n.level, "text": n.text} for n in s.nodes],
            "chrome_guess": s.title is None and not s.cards,
        })
    return {"title": doc.title, "notes": doc.notes, "sections": secs, "page_name": derive_vars(doc).get("page_name", "")}


def template_sections(tpl):
    """Top-level containers -> ordered list of ('widget'|'repeat'|'accordion', element)."""
    out = []
    for i, top in enumerate(tpl.data["content"]):
        items = []

        def visit(el):
            if el.get("elType") == "widget":
                if el["widgetType"] == "nested-accordion":
                    items.append(("accordion", el))
                else:
                    items.append(("widget", el))
                return
            kids = el.get("elements", [])
            wk = [k for k in kids if k.get("elType") == "widget"]
            types = {k["widgetType"] for k in wk}
            if len(wk) >= 2 and len(wk) == len(kids) and len(types) == 1 and next(iter(types)) in GROUP_TYPES:
                items.append(("repeat", el))
                return
            for k in kids:
                visit(k)
        visit(top)
        out.append({"index": i, "id": top["id"], "items": items})
    return out


def widget_current(el):
    wt = el.get("widgetType")
    f = core.TEXT_FIELDS.get(wt, [])
    f = [x for x in f if x != "items"]
    return core.excerpt(el["settings"].get(f[0], ""), 60) if f else ""


def build_rows(tsec, ssec, dvars=None):
    """Suggest bindings for one (template section, source section) pair. Returns (rows, score)."""
    rows, score = [], 0
    dvars = dvars or {}
    cards = ssec.cards if ssec else []
    buttons = list(ssec.buttons) if ssec else []
    has_group = any(k in ("repeat", "accordion") for k, _ in tsec["items"])

    def opts(wt):
        o = [{"v": "", "label": "— keep template text —"}]
        for k, v in dvars.items():
            o.append({"v": f"var.{k}", "label": f"{VAR_DEFS[k]['label']} (from document title): {v}"})
        if not ssec:
            return o
        if ssec.title:
            o.append({"v": "title", "label": "Title: " + core.excerpt(ssec.title.text, 50)})
        if ssec.intro:
            o.append({"v": "paras", "label": f"Paragraphs ({len(ssec.intro)})"})
        if ssec.outro:
            o.append({"v": "outro", "label": f"Trailing paragraphs ({len(ssec.outro)})"})
        for i, b in enumerate(ssec.buttons):
            o.append({"v": f"buttons[{i}]", "label": f"Button {i + 1}: {b.text}"})
        if wt == "text-editor" and len(cards) >= 1:
            o.append({"v": "compose", "label": f"Paragraphs + list of {len(cards)} cards"})
        return o

    heads = [el for k, el in tsec["items"] if k == "widget" and el["widgetType"] == "heading"]
    title_el = max(heads, key=lambda e: len(core.norm(e["settings"].get("title", "")).split()), default=None)
    editor_seen = False
    for kind, el in tsec["items"]:
        if kind == "widget":
            wt = el["widgetType"]
            if wt not in ("heading", "text-editor", "button"):
                continue
            fld = {"heading": "title", "text-editor": "editor", "button": "text"}[wt]
            val = ""
            if ssec:
                if wt == "heading" and el is title_el and ssec.title:
                    val = "title"
                elif wt == "text-editor" and not editor_seen:
                    if cards and not has_group:
                        val = "compose"
                    elif ssec.intro:
                        val = "paras"
                elif wt == "button" and buttons:
                    val = f"buttons[{len(ssec.buttons) - len(buttons)}]"
                    buttons.pop(0)
            if wt == "text-editor":
                editor_seen = True
            if not ssec and not val and wt == "heading" and len(tsec["items"]) == 1 and "last_word" in dvars:
                val = "var.last_word"  # banner-style section: a lone heading with the page name
            score += 1 if val else 0
            rows.append({"kind": "simple", "target": el["id"], "widget": wt, "field": fld,
                         "current": widget_current(el), "value": val, "options": opts(wt)})
        elif kind == "repeat":
            kids = el["elements"]
            wt = kids[0]["widgetType"]
            if wt == "button":
                over, n_items, enabled = "buttons", len(buttons), bool(buttons)
                binds = [{"field": "text", "value": "item.text"}]
                clone_from = 0
                buttons = []
            else:
                over, n_items, enabled = "cards", len(cards), bool(cards)
                if wt == "call-to-action":
                    binds = [{"field": "title", "value": "item.heading"}, {"field": "description", "value": "item.body"}]
                    if any(c.buttons for c in cards):
                        binds.append({"field": "button", "value": "item.button"})
                else:
                    binds = [{"field": "title_text", "value": "item.heading"}, {"field": "description_text", "value": "item.body"}]
                clone_from = len(kids) - 1
            score += 3 if enabled else 0
            rows.append({"kind": "repeat", "container": el["id"], "widget": wt, "over": over, "slots": len(kids),
                         "items": n_items, "binds": binds, "clone_from": clone_from, "enabled": enabled})
        elif kind == "accordion":
            n_tpl = len(el["settings"]["items"])
            enabled = bool(cards)
            score += 3 if enabled else 0
            rows.append({"kind": "accordion", "target": el["id"], "over": "cards", "slots": n_tpl,
                         "items": len(cards), "enabled": enabled})
    return rows, score


def suggest_plan(doc, tpl):
    tsecs = template_sections(tpl)
    srcs = doc.sections
    dv = derive_vars(doc)
    S = [[build_rows(t, s, dv)[1] for s in srcs] for t in tsecs]
    nt, ns = len(tsecs), len(srcs)
    dp = [[0] * (ns + 1) for _ in range(nt + 1)]
    for i in range(1, nt + 1):
        for j in range(1, ns + 1):
            best = max(dp[i - 1][j], dp[i][j - 1])
            if S[i - 1][j - 1] >= 2:
                best = max(best, dp[i - 1][j - 1] + S[i - 1][j - 1])
            dp[i][j] = best
    match, i, j = {}, nt, ns
    while i > 0 and j > 0:
        if S[i - 1][j - 1] >= 2 and dp[i][j] == dp[i - 1][j - 1] + S[i - 1][j - 1]:
            match[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif dp[i][j] == dp[i - 1][j]:
            i -= 1
        else:
            j -= 1
    sections = []
    for t in tsecs:
        s_idx = match.get(t["index"])
        rows, sc = build_rows(t, srcs[s_idx] if s_idx is not None else None, dv)
        sections.append({"t": t["index"], "source": s_idx, "rows": rows, "score": sc})
    ignore = [s.index for s in srcs if s.title is None and not s.cards]
    return {"ignore": ignore, "sections": sections}


def template_view(tpl):
    out = []
    for t in template_sections(tpl):
        ws = []
        for kind, el in t["items"]:
            if kind == "widget":
                ws.append(f"{el['widgetType']} · {widget_current(el)}")
            elif kind == "repeat":
                ws.append(f"[group of {len(el['elements'])} × {el['elements'][0]['widgetType']}]")
            else:
                ws.append(f"[accordion, {len(el['settings']['items'])} items]")
        out.append({"index": t["index"], "id": t["id"], "widgets": ws})
    return out


def plan_to_config(plan, doc, page_title=None):
    srcs = {s.index: s for s in doc.sections}
    rules = []
    used_vars = set()
    for sp in plan["sections"]:
        if sp["source"] is None:
            vb = [{"target": r["target"], "field": r["field"], "value": r["value"]}
                  for r in sp["rows"] if r["kind"] == "simple" and str(r.get("value", "")).startswith("var.")]
            if vb:
                used_vars.update(b["value"][4:] for b in vb)
                rules.append({"name": f"template-section-{sp['t']}", "binds": vb})
            continue
        s = srcs[sp["source"]]
        expect = {k: v for k, v in {"cards": len(s.cards), "paras": len(s.intro), "buttons": len(s.buttons)}.items() if v}
        binds = []
        for r in sp["rows"]:
            if r["kind"] == "simple" and r.get("value"):
                if r["value"] == "compose":
                    binds.append({"target": r["target"], "field": r["field"], "compose": [
                        {"paragraphs": "paras"},
                        {"list": "cards", "item": "<strong>{heading}</strong><br>{body}"}]})
                else:
                    if r["value"].startswith("var."):
                        used_vars.add(r["value"][4:])
                    binds.append({"target": r["target"], "field": r["field"], "value": r["value"]})
            elif r["kind"] == "repeat" and r.get("enabled"):
                binds.append({"repeat": {"over": r["over"], "container": r["container"], "clone_from": r["clone_from"]},
                              "binds": r["binds"]})
            elif r["kind"] == "accordion" and r.get("enabled"):
                binds.append({"accordion": {"target": r["target"], "over": "cards",
                                            "question": "item.heading", "answer": "item.body"}})
        if binds:
            rules.append({"name": f"template-section-{sp['t']}", "section": {"index": s.index, "expect": expect}, "binds": binds})
    cfg = {"name": "generated by ui.py", "version": 1,
           "source": {"adapter": "docx", "options": {}},
           "defaults": {"on_overflow": "clone", "on_underflow": "warn_keep"},
           "ignore": [{"section": i, "reason": "marked as not page content in the UI"} for i in plan.get("ignore", [])],
           "retain": [], "rules": rules}
    if page_title:
        if page_title == derive_vars(doc).get("page_name"):
            # keep it derived so a saved config gives each file its own title
            used_vars.add("page_name")
            cfg["page"] = {"title": "{var.page_name}"}
        else:
            cfg["page"] = {"title": page_title}
    if used_vars:
        cfg["vars"] = {k: {"from": "doc.title", "regex": VAR_DEFS[k]["regex"], "group": 1} for k in sorted(used_vars)}
    return cfg


def result_payload(eng, res, cfg):
    return {
        "ok": not res["errors"],
        "counts": {
            "written": sum(1 for r in eng.log if r["status"] == "mapped"),
            "unchanged": sum(1 for r in eng.log if r["status"].startswith("unchanged")),
            "clones": len(eng.clones), "warnings": len(res["warnings"]), "errors": len(res["errors"]),
        },
        "errors": res["errors"], "warnings": res["warnings"], "checks": res["checks"],
        "mapping": [{k: v for k, v in r.items() if not k.startswith("_")} for r in eng.log],
        "unmapped_sections": [{"index": s.index, "text": core.sec_text(s)} for s in res["unmapped_sections"]],
        "unmapped_nodes": [{"section": s.index, "kind": n.kind, "text": n.text} for s, n in res["unmapped_nodes"]],
        "retained": res["retained"], "media": res["media"],
        "output": eng.tpl.data, "config": cfg,
    }



PV_FIELDS = {"heading": ["title"], "text-editor": ["editor"], "button": ["text"],
             "call-to-action": ["title", "description", "button"], "image-box": ["title_text", "description_text"],
             "shortcode": ["shortcode"], "template": ["template_id"]}


def preview_tree(eng, res):
    """Structure of the generated page for the section preview: widget types, ids and where content landed."""
    out = eng.tpl.data
    clone_ids = {c["id"] for c in eng.clones}
    written = {}
    for (i, f) in eng.written:
        written.setdefault(i, set()).add(f)
    tgt, derived = {}, set()
    for r in eng.log:
        if r["section"] is not None:
            tgt.setdefault(r["target"], set()).add(r["section"])
        elif r["target"] != "(page)":
            derived.add(r["target"])
    counts = {"new": 0, "keep": 0, "cloned": 0}

    def first_editor(el):
        for c in el.get("elements", []):
            if c.get("widgetType") == "text-editor":
                return c
            r = first_editor(c)
            if r:
                return r
        return None

    def node(el):
        w, st = el.get("widgetType"), el.get("settings", {})
        n = {"id": el["id"], "el": el.get("elType"), "w": w, "clone": el["id"] in clone_ids,
             "written": sorted(written.get(el["id"], [])), "sources": set(tgt.get(el["id"], [])),
             "derived": el["id"] in derived}
        if n["el"] == "widget":
            f = {k: str(st.get(k, "")) for k in PV_FIELDS.get(w, [])}
            if w == "heading":
                f["tag"] = st.get("header_size", "h2")
            if w == "image":
                f["url"] = (st.get("image") or {}).get("url", "")
            if w == "nested-accordion":
                items = []
                for i, it in enumerate(st.get("items", [])):
                    kid = el["elements"][i] if i < len(el.get("elements", [])) else None
                    ed = first_editor(kid) if kid else None
                    items.append({"title": it.get("item_title", ""), "answer": ed["settings"].get("editor", "") if ed else "",
                                  "clone": bool(kid and kid["id"] in clone_ids),
                                  "filled": (el["id"], "items") in eng.written})
                f["items"] = items
                if (el["id"], "items") in eng.written:
                    n["written"] = ["items"]
            n["f"] = f
            counts["cloned" if n["clone"] else ("new" if n["written"] else "keep")] += 1
        else:
            kids = [node(c) for c in el.get("elements", [])]
            wk = [k for k in kids if k["el"] == "widget"]
            n["group"] = len(wk) >= 2 and len(wk) == len(kids) and len({k["w"] for k in wk}) == 1 and wk[0]["w"] in GROUP_TYPES
            n["dir"] = st.get("flex_direction", "column")
            n["kids"] = kids
            for k in kids:
                n["sources"] |= set(k["sources"])
                n["derived"] = n["derived"] or k["derived"]
        n["sources"] = sorted(n["sources"])
        return n

    sections = [{"index": i, "node": node(top)} for i, top in enumerate(out["content"])]
    for sc in sections:
        sc["sources"] = sc["node"]["sources"]
        sc["derived"] = sc["node"]["derived"]
    return {
        "sections": sections, "counts": counts,
        "source_titles": {s.index: (s.title.text if s.title else "(no title)") for s in eng.doc.sections},
        "unplaced": [{"index": s.index, "title": s.title.text if s.title else "(no title)"} for s in res["unmapped_sections"]],
        "ignored": [{"index": s.index, "title": s.title.text if s.title else "(no title)", "reason": s.ignored}
                    for s in eng.doc.sections if s.ignored],
    }


# ----------------------------------------------------------------------------
# multi-file helpers
# ----------------------------------------------------------------------------
def copy_plan(plan, doc, tpl):
    """Re-apply one file's mapping choices to another file's document (same template)."""
    dv = derive_vars(doc)
    tsecs = template_sections(tpl)
    srcs = {s.index: s for s in doc.sections}
    out = {"ignore": [i for i in plan.get("ignore", []) if i in srcs], "sections": []}
    for sp in plan["sections"]:
        s_idx = sp["source"] if sp["source"] in srcs else None
        rows, score = build_rows(tsecs[sp["t"]], srcs.get(s_idx), dv)
        old = {(r["kind"], r.get("target") or r.get("container")): r for r in sp["rows"]}
        for r in rows:
            o = old.get((r["kind"], r.get("target") or r.get("container")))
            if not o:
                continue
            if r["kind"] == "simple":
                if o["value"] == "" or any(op["v"] == o["value"] for op in r["options"]):
                    r["value"] = o["value"]
            else:
                r["enabled"] = bool(o["enabled"]) and r["items"] > 0
        out["sections"].append({"t": sp["t"], "source": s_idx, "rows": rows, "score": score})
    return out


def safe_stem(name):
    stem = re.sub(r"\.docx$", "", name, flags=re.I)
    return re.sub(r"[^\w.\- ]+", "_", stem).strip() or "output"


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------
class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
            fn = {"/api/analyze": self.analyze, "/api/rows": self.rows, "/api/copy_plan": self.copy,
                  "/api/generate_batch": self.generate_batch}[self.path]
            self._send(200, json.dumps(fn(data), ensure_ascii=False))
        except Exception as e:
            traceback.print_exc()
            self._send(400, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    # -- endpoints
    def analyze(self, d):
        tpl_data = json.loads(d["template"])
        if "content" not in tpl_data:
            raise ValueError("template JSON has no 'content' key - is it an Elementor template export?")
        tpl = core.Template(tpl_data)
        cfg = json.loads(d["config"]) if d.get("config") else None
        opts = ((cfg or {}).get("source") or {}).get("options")
        files = []
        for item in d["docs"]:
            try:
                docx = base64.b64decode(item["b64"])
                doc = core.parse_docx(io.BytesIO(docx), opts)
                sid = uuid.uuid4().hex
                SESSIONS[sid] = {"docx": docx, "tpl_data": tpl_data, "doc": doc, "tpl": tpl, "name": item["name"]}
                files.append({"sid": sid, "name": item["name"], "doc": doc_summary(doc),
                              "plan": None if cfg else suggest_plan(doc, tpl)})
            except Exception as e:
                files.append({"name": item["name"], "error": f"{type(e).__name__}: {e}"})
        return {"template": template_view(tpl), "files": files, "saved_config": cfg}

    def rows(self, d):
        s = SESSIONS[d["sid"]]
        tsec = template_sections(s["tpl"])[d["t"]]
        src = None if d["source"] is None else next(x for x in s["doc"].sections if x.index == d["source"])
        rows, score = build_rows(tsec, src, derive_vars(s["doc"]))
        return {"rows": rows, "score": score}

    def copy(self, d):
        """d: {plan, targets:[sid,...]} -> {sid: plan}"""
        out = {}
        for sid in d["targets"]:
            s = SESSIONS[sid]
            out[sid] = copy_plan(d["plan"], s["doc"], s["tpl"])
        return {"plans": out}

    def generate_batch(self, d):
        import zipfile
        from types import SimpleNamespace
        results, used = [], set()
        buf = io.BytesIO()
        zf = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
        for it in d["items"]:
            s = SESSIONS.get(it["sid"])
            name = s["name"] if s else it.get("name", "?")
            try:
                cfg = d["config"] if d.get("config") else plan_to_config(it["plan"], s["doc"], it.get("page_title") or None)
                eng, res = core.run_mapping(io.BytesIO(s["docx"]), s["tpl_data"], cfg)
                stem, k = safe_stem(name), 1
                while stem in used:
                    k += 1
                    stem = f"{safe_stem(name)}-{k}"
                used.add(stem)
                payload = result_payload(eng, res, cfg)
                ns = SimpleNamespace(content=name, template=d.get("template_name", "template.json"),
                                     mapping="(web UI)", out=stem + ".json")
                payload["report_md"] = core.build_report(eng, res, ns)
                payload["preview"] = preview_tree(eng, res)
                payload.update({"name": name, "stem": stem, "sid": it["sid"]})
                zf.writestr(f"{stem}/{stem}.json", json.dumps(eng.tpl.data, ensure_ascii=False, indent=2))
                zf.writestr(f"{stem}/{stem}.report.md", payload["report_md"])
                zf.writestr(f"{stem}/{stem}.mapping.json", json.dumps(cfg, ensure_ascii=False, indent=2))
                results.append(payload)
            except Exception as e:
                traceback.print_exc()
                results.append({"name": name, "stem": None, "failed": f"{type(e).__name__}: {e}"})
        zf.close()
        return {"results": results, "zip_b64": base64.b64encode(buf.getvalue()).decode()}


# ----------------------------------------------------------------------------
# front-end
# ----------------------------------------------------------------------------
PAGE = r"""<!doctype html>
<html lang="en" data-theme="auto"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content → JSON Mapper</title>
<style>
:root{--bg:#f4f5fa;--panel:#fff;--ink:#161a25;--mut:#69728a;--line:#e3e6ef;--soft:#eef0f7;--acc:#4f46e5;--acc2:#6d64f0;--accsoft:#ecebff;--ok:#0f8a5f;--oksoft:#e2f5ec;--warn:#b45309;--warnsoft:#fdf0dc;--err:#c5392b;--errsoft:#fde8e5;--sh:0 1px 2px rgba(16,24,40,.06),0 6px 20px rgba(16,24,40,.05);--r:12px}
:root[data-theme=dark]{--bg:#0f121a;--panel:#171b26;--ink:#e9ecf5;--mut:#94a0b8;--line:#272d3d;--soft:#1e2433;--acc:#8b86ff;--acc2:#a29eff;--accsoft:#25264a;--ok:#4cc79a;--oksoft:#12302a;--warn:#f0a95a;--warnsoft:#3a2a14;--err:#ff7b6b;--errsoft:#3b1d1a;--sh:0 1px 2px rgba(0,0,0,.4),0 6px 20px rgba(0,0,0,.3)}
@media(prefers-color-scheme:dark){:root[data-theme=auto]{--bg:#0f121a;--panel:#171b26;--ink:#e9ecf5;--mut:#94a0b8;--line:#272d3d;--soft:#1e2433;--acc:#8b86ff;--acc2:#a29eff;--accsoft:#25264a;--ok:#4cc79a;--oksoft:#12302a;--warn:#f0a95a;--warnsoft:#3a2a14;--err:#ff7b6b;--errsoft:#3b1d1a;--sh:0 1px 2px rgba(0,0,0,.4),0 6px 20px rgba(0,0,0,.3)}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
button,input,select{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.hidden{display:none!important}.mut{color:var(--mut)}.ok{color:var(--ok)}.warn{color:var(--warn)}.err{color:var(--err)}.sp{flex:1}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}
/* top bar */
.bar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:20px;padding:10px 24px;background:var(--panel);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;min-width:0}.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--acc),var(--acc2));color:#fff;display:grid;place-items:center;font-weight:700;font-size:16px}
.brand b{display:block;line-height:1.2}.brand small{color:var(--mut);display:block;line-height:1.2}
.steps{display:flex;gap:4px;margin:0 auto}.step{display:flex;align-items:center;gap:8px;padding:6px 12px;border:0;background:transparent;border-radius:999px;cursor:pointer;color:var(--mut);font-weight:600}
.step i{font-style:normal;width:22px;height:22px;border-radius:50%;display:grid;place-items:center;font-size:12px;background:var(--soft);color:var(--mut)}
.step.on{background:var(--accsoft);color:var(--acc)}.step.on i{background:var(--acc);color:#fff}.step.done i{background:var(--oksoft);color:var(--ok)}
.step:disabled{opacity:.4;cursor:default}
.ghost{background:transparent;border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer}
main{max-width:1120px;margin:0 auto;padding:22px 20px 40px}
/* ui atoms */
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);margin-bottom:14px}.pad{padding:16px 18px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:15px;margin:0 0 8px}.lead{color:var(--mut);margin:0 0 18px;max-width:70ch}
.btn{background:var(--acc);color:#fff;border:0;border-radius:9px;padding:9px 16px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.btn:hover{background:var(--acc2)}.btn.sec{background:transparent;color:var(--acc);border:1px solid var(--line)}.btn.sec:hover{background:var(--accsoft)}
.btn.sm{padding:4px 10px;font-size:12px;border-radius:7px}.btn:disabled{opacity:.45;cursor:default}
.chip{display:inline-flex;align-items:center;gap:4px;padding:1px 9px;border-radius:999px;font-size:12px;font-weight:600;background:var(--soft);color:var(--mut);white-space:nowrap}
.chip.ok{background:var(--oksoft);color:var(--ok)}.chip.warn{background:var(--warnsoft);color:var(--warn)}.chip.err{background:var(--errsoft);color:var(--err)}.chip.acc{background:var(--accsoft);color:var(--acc)}
select,input[type=text]{padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--panel);max-width:100%}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
details>summary{cursor:pointer;list-style:none}details>summary::-webkit-details-marker{display:none}
details>summary:before{content:"▸";display:inline-block;width:14px;color:var(--mut);transition:transform .15s}details[open]>summary:before{transform:rotate(90deg)}
/* upload */
.zones{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}
.zone{display:block;border:2px dashed var(--line);border-radius:var(--r);padding:20px;text-align:center;cursor:pointer;background:var(--panel);transition:.15s}
.zone:hover,.zone.over{border-color:var(--acc);background:var(--accsoft)}.zone .ic{font-size:28px}.zone b{display:block;margin-top:4px}.zone small{color:var(--mut)}
.zone.has{border-style:solid;border-color:var(--ok)}
.flist{margin-top:10px;text-align:left}.fitem{display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:8px;background:var(--soft);margin-top:4px;font-size:13px}
.fitem span.n{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}.fitem button{border:0;background:transparent;color:var(--mut);cursor:pointer;font-size:16px}
.how{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:22px}.how div{padding:12px 14px;border-radius:10px;background:var(--soft)}.how b{display:block}
/* file pills */
.files{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}.fp{display:flex;align-items:center;gap:6px;padding:6px 12px;border:1px solid var(--line);border-radius:999px;cursor:pointer;background:var(--panel);font-weight:500}
.fp.on{border-color:var(--acc);background:var(--accsoft);color:var(--acc)}.dot{width:8px;height:8px;border-radius:50%;background:var(--line)}.dot.ok{background:var(--ok)}.dot.warn{background:var(--warn)}.dot.err{background:var(--err)}
/* mapping */
.strip{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.tsec-h{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line)}
.num{width:30px;height:30px;border-radius:8px;background:var(--soft);display:grid;place-items:center;font-weight:700;color:var(--mut)}.tsec.active .num{background:var(--acc);color:#fff}
.tsec-t{flex:1;min-width:200px}.wch{display:flex;gap:4px;flex-wrap:wrap;margin-top:3px}
.rowx{display:grid;grid-template-columns:minmax(0,1.1fr) 20px minmax(0,1fr);gap:8px;align-items:center;padding:7px 16px;border-bottom:1px solid var(--line)}
.rowx:last-of-type{border-bottom:0}.rowx .l{min-width:0}.rowx .cur{display:block;color:var(--mut);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.arrow{color:var(--mut);text-align:center}
.rowx select{width:100%}.sw{display:flex;align-items:center;gap:8px}
.srcv{padding:0 16px 12px}.srcv summary{padding:8px 0;color:var(--acc);font-weight:600;font-size:13px}
.nodes{background:var(--soft);border-radius:8px;padding:8px 10px;max-height:260px;overflow:auto}.nd{padding:2px 0;display:flex;gap:8px}.nd .k{flex:none;min-width:34px;text-align:center;border-radius:5px;font-size:10px;font-weight:700;padding:1px 4px;background:var(--panel);color:var(--mut);height:18px}
.nd .k.heading{background:var(--accsoft);color:var(--acc)}.nd .k.button{background:var(--oksoft);color:var(--ok)}.nd .k.placeholder{background:var(--warnsoft);color:var(--warn)}
.dock{position:sticky;bottom:0;z-index:10;margin:18px -20px -40px;padding:12px 20px;background:var(--panel);border-top:1px solid var(--line);box-shadow:0 -6px 20px rgba(16,24,40,.06)}
.dock .in{max-width:1120px;margin:auto;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
/* results */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}.tile{padding:14px 16px}.tile b{display:block;font-size:26px;line-height:1.1}.tile span{color:var(--mut);font-size:12px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--mut);font-weight:600;font-size:12px;background:var(--soft)}
.det{padding:4px 18px 14px}.det h3{font-size:13px;margin:14px 0 6px}.det ul{margin:4px 0;padding-left:18px}.det pre{background:var(--soft);padding:8px;border-radius:8px;white-space:pre-wrap;font-size:12px}
.tbl-wrap{overflow:auto}
/* preview */
.pvgrid2{display:grid;grid-template-columns:230px minmax(0,1fr);gap:16px;align-items:start}
.toc{position:sticky;top:76px;max-height:calc(100vh - 100px);overflow:auto;padding:10px}.toc a{display:flex;gap:8px;align-items:center;padding:6px 8px;border-radius:8px;color:var(--ink);text-decoration:none;font-size:13px;cursor:pointer}
.toc a:hover{background:var(--soft)}.toc small{color:var(--mut);display:block}
.pvh{font-weight:700}.pvh.h1{font-size:22px}.pvh.h2{font-size:19px}.pvh.h3{font-size:16px}.pvh.h4,.pvh.h5,.pvh.h6{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut)}
.pvct{display:flex;flex-direction:column;gap:8px;border:1px dashed var(--line);border-radius:10px;padding:8px;margin:6px 0}
.pvct.pvrow{flex-direction:row;flex-wrap:wrap}.pvct.pvrow>*{flex:1 1 240px}.pvct.pvgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
.pvw{position:relative;border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:8px 10px;background:var(--panel)}
.pvw.new{border-left-color:var(--ok)}.pvw.cl{border-left-color:var(--warn);background:var(--warnsoft)}.pvw.keep{border-left-color:#9aa3b2}
.dimkeep .pvw.keep{opacity:.38}
.pvchip{font-size:11px;color:var(--mut);margin-bottom:4px}.pvchip b{color:var(--ink);font-family:ui-monospace,Menlo,Consolas,monospace}
.pvbtn{display:inline-block;background:var(--acc);color:#fff;border-radius:999px;padding:4px 14px;font-weight:600;font-size:12px;margin-top:4px}
.pvtxt p{margin:4px 0}.pvtxt ul{margin:4px 0;padding-left:20px}.pvcard{border:1px solid var(--line);border-radius:8px;padding:8px}
.pvimg{background:var(--soft);border:1px dashed var(--line);border-radius:8px;padding:14px;text-align:center;color:var(--mut);font-size:12px}
.pvacc{border:1px solid var(--line);border-left:3px solid var(--ok);border-radius:8px;padding:6px 8px;margin:4px 0}.pvacc.cl{border-left-color:var(--warn)}
.lg{display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:12px}.lg i{display:inline-block;width:12px;height:12px;border-radius:3px}
/* overlays */
.busy{position:fixed;inset:0;z-index:50;background:rgba(15,18,26,.45);display:grid;place-items:center}
.busy>div{background:var(--panel);padding:18px 26px;border-radius:12px;display:flex;gap:12px;align-items:center;box-shadow:var(--sh)}
.spin{width:20px;height:20px;border-radius:50%;border:3px solid var(--line);border-top-color:var(--acc);animation:sp 0.8s linear infinite}@keyframes sp{to{transform:rotate(360deg)}}
#toasts{position:fixed;right:16px;bottom:16px;z-index:60;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--ink);color:var(--bg);padding:10px 14px;border-radius:10px;max-width:380px;box-shadow:var(--sh)}.toast.ok{background:var(--ok);color:#fff}.toast.warn{background:var(--warn);color:#fff}.toast.err{background:var(--err);color:#fff}
.empty{text-align:center;padding:40px 20px;color:var(--mut)}
@media(max-width:860px){.steps .step span{display:none}.pvgrid2{grid-template-columns:1fr}.toc{position:static;max-height:none}.rowx{grid-template-columns:1fr}.arrow{display:none}.bar{padding:10px 14px}.brand small{display:none}}
</style></head><body>
<header class="bar">
  <div class="brand"><div class="logo">⇄</div><div><b>Content → JSON Mapper</b><small>Word content → Elementor template</small></div></div>
  <nav class="steps" id="steps" aria-label="Steps"></nav>
  <button class="ghost" id="theme" title="Toggle light / dark">◐</button>
</header>
<main>
  <section id="v_files" class="view">
    <h1>Map Word content into your Elementor template</h1>
    <p class="lead">Drop one or many content files and the template. The tool suggests which content goes in which section, lets you adjust it, previews the result and exports valid JSON. Everything runs on your computer.</p>
    <div class="zones">
      <div><label class="zone" id="zDocx" for="fDocx"><div class="ic">📄</div><b>Content files</b><small>.docx — drop here or click, many allowed</small></label>
        <input type="file" id="fDocx" accept=".docx" multiple class="hidden"><div class="flist" id="lDocx"></div></div>
      <div><label class="zone" id="zTpl" for="fTpl"><div class="ic">🧩</div><b>Elementor template</b><small>.json export — one template for all files</small></label>
        <input type="file" id="fTpl" accept=".json" class="hidden"><div class="flist" id="lTpl"></div></div>
      <div><label class="zone" id="zCfg" for="fCfg"><div class="ic">⚙️</div><b>Saved mapping <span class="mut">(optional)</span></b><small>reuse a downloaded mapping config for same-layout files</small></label>
        <input type="file" id="fCfg" accept=".json" class="hidden"><div class="flist" id="lCfg"></div></div>
    </div>
    <div class="row" style="margin-top:18px"><button class="btn" id="bAn" disabled>Analyze files →</button><span id="anMsg" class="mut"></span></div>
    <div class="how"><div><b>1 · Analyze</b><span class="mut">Reads sections, headings, paragraphs, cards and buttons.</span></div><div><b>2 · Map</b><span class="mut">Review the auto-suggested mapping and tweak any dropdown.</span></div><div><b>3 · Preview</b><span class="mut">See which Elementor widget received which content.</span></div><div><b>4 · Export</b><span class="mut">Download each JSON or everything as one ZIP.</span></div></div>
  </section>
  <section id="v_map" class="view hidden"></section>
  <section id="v_prev" class="view hidden"></section>
  <section id="v_res" class="view hidden"></section>
</main>
<div id="busy" class="busy hidden"><div><span class="spin"></span><span id="busyMsg">Working…</span></div></div>
<div id="toasts"></div>
<script>
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const kb=n=>n<1024?n+' B':n<1048576?(n/1024).toFixed(1)+' KB':(n/1048576).toFixed(1)+' MB';
let S={step:'files',tpl:[],files:[],cur:0,cfg:null,tplName:'template.json',results:null,previews:{},open:{},up:{docx:[],tpl:null,cfg:null}};
const F=()=>S.files[S.cur],okFiles=()=>S.files.filter(f=>!f.error);

/* ---------- helpers ---------- */
function toast(msg,tone,ms){const t=document.createElement('div');t.className='toast '+(tone||'');t.textContent=msg;$('#toasts').appendChild(t);setTimeout(()=>t.remove(),ms||4500)}
function busy(on,msg){$('#busy').classList.toggle('hidden',!on);if(msg)$('#busyMsg').textContent=msg}
function readFile(f,b64){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(b64?r.result.split(',')[1]:r.result);r.onerror=rej;b64?r.readAsDataURL(f):r.readAsText(f)})}
async function api(path,body){const r=await fetch(path,{method:'POST',body:JSON.stringify(body)});const j=await r.json();if(j.error)throw new Error(j.error);return j}
function dlBlob(name,blob){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click()}
function dl(name,text,type){dlBlob(name,new Blob([text],{type:type||'application/json'}))}
function b64Blob(b64,type){const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);return new Blob([u],{type})}
function keepScroll(fn){const y=window.scrollY;fn();window.scrollTo(0,y)}
$('#theme').onclick=()=>{const r=document.documentElement;const dark=r.dataset.theme==='dark'||(r.dataset.theme==='auto'&&matchMedia('(prefers-color-scheme:dark)').matches);r.dataset.theme=dark?'light':'dark'};

/* ---------- navigation ---------- */
const STEPS=[['files','Files'],['map','Mapping'],['prev','Preview'],['res','Results']];
function stepEnabled(k){return k==='files'||(k==='map'&&okFiles().length>0)||(k==='prev'&&okFiles().length>0)||(k==='res'&&!!S.results)}
function renderSteps(){const idx=STEPS.findIndex(s=>s[0]===S.step);
  $('#steps').innerHTML=STEPS.map((s,i)=>`<button class="step${s[0]===S.step?' on':''}${i<idx&&stepEnabled(s[0])?' done':''}" data-s="${s[0]}" ${stepEnabled(s[0])?'':'disabled'} ${s[0]===S.step?'aria-current="step"':''}><i>${i<idx&&stepEnabled(s[0])?'✓':i+1}</i><span>${s[1]}</span></button>`).join('');
  $$('#steps .step').forEach(b=>b.onclick=()=>go(b.dataset.s))}
function go(step){S.step=step;$$('.view').forEach(v=>v.classList.toggle('hidden',v.id!=='v_'+step));renderSteps();renderCurrent();window.scrollTo(0,0)}
function renderCurrent(){({files:()=>{},map:renderMap,prev:renderPrev,res:renderRes})[S.step]()}

/* ---------- 1. upload ---------- */
function renderUp(){
  const L=(el,items,rm)=>{el.innerHTML=items.map((f,i)=>`<div class="fitem"><span>${f.name.endsWith('.json')?'🧩':'📄'}</span><span class="n" title="${esc(f.name)}">${esc(f.name)}</span><span class="mut">${kb(f.size)}</span><button data-rm="${rm}" data-i="${i}" title="Remove" aria-label="Remove ${esc(f.name)}">×</button></div>`).join('')};
  L($('#lDocx'),S.up.docx,'docx');L($('#lTpl'),S.up.tpl?[S.up.tpl]:[],'tpl');L($('#lCfg'),S.up.cfg?[S.up.cfg]:[],'cfg');
  $('#zDocx').classList.toggle('has',S.up.docx.length>0);$('#zTpl').classList.toggle('has',!!S.up.tpl);$('#zCfg').classList.toggle('has',!!S.up.cfg);
  $('#bAn').disabled=!(S.up.docx.length&&S.up.tpl);
  $$('#v_files [data-rm]').forEach(b=>b.onclick=()=>{const i=+b.dataset.i;if(b.dataset.rm==='docx')S.up.docx.splice(i,1);else S.up[b.dataset.rm]=null;renderUp()})}
function addFiles(kind,list){list=[...list];
  if(kind==='docx'){for(const f of list){if(!/\.docx$/i.test(f.name)){toast(f.name+' is not a .docx file','warn');continue}if(!S.up.docx.some(x=>x.name===f.name&&x.size===f.size))S.up.docx.push(f)}}
  else if(list[0]){if(!/\.json$/i.test(list[0].name)){toast(list[0].name+' is not a .json file','warn');return}S.up[kind]=list[0]}
  renderUp()}
[['docx','fDocx','zDocx'],['tpl','fTpl','zTpl'],['cfg','fCfg','zCfg']].forEach(([k,i,z])=>{
  $('#'+i).addEventListener('change',e=>{addFiles(k,e.target.files);try{e.target.value=''}catch(_){}});
  const zn=$('#'+z);['dragenter','dragover'].forEach(ev=>zn.addEventListener(ev,e=>{e.preventDefault();zn.classList.add('over')}));
  ['dragleave','drop'].forEach(ev=>zn.addEventListener(ev,e=>{e.preventDefault();zn.classList.remove('over')}));
  zn.addEventListener('drop',e=>addFiles(k,e.dataTransfer.files))});
$('#bAn').onclick=async()=>{
  $('#anMsg').textContent='';busy(true,'Analyzing '+S.up.docx.length+' file(s)…');
  try{
    const docs=[];for(const f of S.up.docx)docs.push({name:f.name,b64:await readFile(f,true)});
    const j=await api('/api/analyze',{docs,template:await readFile(S.up.tpl),config:S.up.cfg?await readFile(S.up.cfg):null});
    S={...S,tpl:j.template,files:j.files,cur:Math.max(0,j.files.findIndex(f=>!f.error)),cfg:j.saved_config,tplName:S.up.tpl.name,results:null,previews:{},open:{}};
    const bad=S.files.filter(f=>f.error);
    bad.forEach(f=>toast(f.name+': '+f.error,'err',7000));
    if(!okFiles().length){$('#anMsg').innerHTML='<span class="err">None of the files could be read.</span>';renderSteps();return}
    toast(okFiles().length+' file(s) analyzed'+(bad.length?', '+bad.length+' failed':''),bad.length?'warn':'ok');go('map');
  }catch(e){$('#anMsg').innerHTML='<span class="err">'+esc(e.message)+'</span>'}
  finally{busy(false)}};

/* ---------- shared: file bar ---------- */
function fileBar(){
  if(S.files.length<2&&!S.files.some(f=>f.error))return '';
  return '<div class="files">'+S.files.map((f,i)=>{const r=S.results&&S.results.results.find(x=>x.name===f.name&&(x.sid===f.sid||!x.sid));
    const tone=f.error?'err':(r?(r.failed||!r.ok?'err':(r.counts.warnings?'warn':'ok')):'');
    return `<div class="fp${i===S.cur?' on':''}" data-i="${i}" title="${esc(f.error||f.name)}"><span class="dot ${tone}"></span>${esc(f.name)}</div>`}).join('')+'</div>'}
function bindFileBar(root){$$('.fp',root).forEach(p=>p.onclick=()=>{const i=+p.dataset.i;if(S.files[i].error){toast(S.files[i].name+': '+S.files[i].error,'err',7000);return}S.cur=i;renderCurrent()})}

/* ---------- 2. mapping ---------- */
const activeRows=sp=>sp.rows.filter(r=>r.kind==='simple'?!!r.value:r.enabled);
function widgetChips(ws){const seen=[];ws.forEach(w=>{let t;const m=w.match(/^\[group of (\d+) × (.+)\]$/);if(m)t=m[2]+' ×'+m[1];else if(w.startsWith('[accordion'))t='accordion';else t=w.split(' · ')[0];if(!seen.includes(t))seen.push(t)});return seen.slice(0,8).map(t=>`<span class="chip">${esc(t)}</span>`).join('')}
function srcOptions(sel){return '<option value="">— none (keep template) —</option>'+F().doc.sections.map(s=>`<option value="${s.index}"${sel===s.index?' selected':''}>Content ${s.index} · ${esc((s.title||'(no title)').slice(0,60))}</option>`).join('')}
function nodesHtml(s){return '<div class="nodes">'+s.nodes.map(n=>`<div class="nd"><span class="k ${n.kind}">${n.kind==='heading'?'H'+n.level:n.kind==='paragraph'?'P':n.kind==='listitem'?'LI':n.kind==='button'?'BTN':n.kind==='placeholder'?'PH':'TXT'}</span><span>${esc(n.text)}</span></div>`).join('')+'</div>'}
function genLabel(){const n=okFiles().length;return n>1?`Generate all ${n} files`:'Generate JSON'}
function renderMap(){keepScroll(()=>{
  const root=$('#v_map'),f=F();if(!f){root.innerHTML='<div class="empty">Analyze files first.</div>';return}
  if(S.cfg){root.innerHTML=fileBar()+`<div class="card pad"><h2>Saved mapping config loaded</h2><p class="mut">It has <b>${S.cfg.rules.length}</b> rules and will be applied as-is to <b>${okFiles().length}</b> file(s). To edit mappings here instead, go back and analyze without a config.</p><div class="row"><button class="btn sec" id="bPrev">Preview this file</button><button class="btn" id="bGen">${genLabel()}</button></div></div>`;
    bindFileBar(root);$('#bGen').onclick=generate;$('#bPrev').onclick=previewFile;return}
  const plan=f.plan,used=new Set(plan.sections.filter(sp=>sp.source!==null&&activeRows(sp).length).map(sp=>sp.source));
  const mapped=plan.sections.filter(sp=>activeRows(sp).length).length;
  const unplaced=f.doc.sections.filter(s=>!plan.ignore.includes(s.index)&&!used.has(s.index));
  let h=fileBar()+`<div class="strip"><span class="chip ok">${mapped} of ${plan.sections.length} template sections filled</span>`+
    (unplaced.length?`<span class="chip warn" title="${esc(unplaced.map(s=>'Content '+s.index+' '+(s.title||'(no title)')).join(' | '))}">⚠ ${unplaced.length} content section(s) not placed</span>`:'<span class="chip ok">all content placed</span>')+
    `<span class="sp"></span><span class="mut">${esc(f.name)}</span></div><div class="mut" style="margin:-6px 0 12px">“Content N” = the Nth block of your Word file, counted from 0 (open “Source content” under a card to see it). “Template section N” = the Nth section of the Elementor template.</div>`;
  h+=`<div class="card pad"><h2>Not page content (ignored)</h2><div class="mut" style="margin-bottom:8px">Tick sections that are header, menu or footer. Ignored sections are skipped; anything else that stays unmapped is reported.</div><div class="row">`+
     f.doc.sections.map(s=>`<label class="chip ${plan.ignore.includes(s.index)?'acc':''}" style="cursor:pointer"><input type="checkbox" class="ig" data-i="${s.index}" ${plan.ignore.includes(s.index)?'checked':''}> Content ${s.index} ${esc((s.title||'(no title)').slice(0,26))}</label>`).join('')+`</div></div>`;
  plan.sections.forEach((sp,si)=>{const tv=S.tpl[sp.t],act=activeRows(sp).length,key=f.sid+':'+sp.t;
    h+=`<section class="card tsec${act?' active':''}"><div class="tsec-h"><span class="num">${sp.t}</span><div class="tsec-t"><b>Template section ${sp.t}</b> ${act?`<span class="chip ok">${sp.source!==null?'from Content '+sp.source:'derived'}</span>`:'<span class="chip">template as-is</span>'}<div class="wch">${widgetChips(tv.widgets)}</div></div>`+
      `<label class="mut">Fill from <select class="srcsel" data-si="${si}">${srcOptions(sp.source)}</select></label></div>`;
    if(sp.rows.length)sp.rows.forEach((r,ri)=>{
      if(r.kind==='simple')h+=`<div class="rowx"><div class="l"><code>${esc(r.widget+'.'+r.field)}</code><span class="cur" title="${esc(r.current)}">${esc(r.current)}</span></div><span class="arrow">←</span><select class="rowsel" data-si="${si}" data-ri="${ri}">${r.options.map(o=>`<option value="${esc(o.v)}"${o.v===r.value?' selected':''}>${esc(o.label)}</option>`).join('')}</select></div>`;
      else{const what=r.kind==='accordion'?'Accordion items (question + answer)':`Group of ${r.slots} × ${r.widget}`;
        const note=r.items>r.slots?`${r.items-r.slots} extra will be cloned`:(r.items<r.slots&&r.items>0?`${r.slots-r.items} slot(s) keep template text`:'');
        h+=`<div class="rowx"><div class="l"><b>${esc(what)}</b> <span class="chip acc">repeat</span><span class="cur">${r.kind==='accordion'?'':'← '+esc(r.over)+' · '}${r.items} source item(s)${note?' · '+esc(note):''}</span></div><span class="arrow">←</span><label class="sw"><input type="checkbox" class="rowck" data-si="${si}" data-ri="${ri}" ${r.enabled?'checked':''}> Fill this group</label></div>`}});
    else h+='<div class="rowx"><span class="mut">No mappable text widgets in this section.</span></div>';
    if(sp.source!==null){const s=f.doc.sections.find(x=>x.index===sp.source);if(s)h+=`<details class="srcv" data-k="${key}"${S.open[key]?' open':''}><summary>Show what Content ${s.index} contains <span class="mut">· paragraphs ${s.counts.paras} · cards ${s.counts.cards} · buttons ${s.counts.buttons}</span></summary>${nodesHtml(s)}</details>`}
    h+='</section>'});
  const multi=okFiles().length>1;
  h+=`<div class="dock"><div class="in"><label class="mut">Page title <input id="pgTitle" type="text" placeholder="optional" value="${esc(f.pageTitle??f.doc.page_name??'')}" style="width:220px"></label><span class="sp"></span>`+
     (multi?'<button class="btn sec" id="bCopy" title="Apply this file\'s choices to every other file">Copy mapping to other files</button>':'')+
     `<button class="btn sec" id="bCfg">Download mapping</button><button class="btn sec" id="bPrev">Preview this file</button><button class="btn" id="bGen">${genLabel()} →</button></div></div>`;
  root.innerHTML=h;bindFileBar(root);
  $$('.ig',root).forEach(c=>c.onchange=()=>{const i=+c.dataset.i;plan.ignore=plan.ignore.filter(x=>x!==i);if(c.checked)plan.ignore.push(i);renderMap()});
  $$('.rowsel',root).forEach(s=>s.onchange=()=>{plan.sections[+s.dataset.si].rows[+s.dataset.ri].value=s.value;renderMap()});
  $$('.rowck',root).forEach(c=>c.onchange=()=>{plan.sections[+c.dataset.si].rows[+c.dataset.ri].enabled=c.checked;renderMap()});
  $$('.srcsel',root).forEach(s=>s.onchange=async()=>{const sp=plan.sections[+s.dataset.si];sp.source=s.value===''?null:+s.value;
    try{const j=await api('/api/rows',{sid:f.sid,t:sp.t,source:sp.source});sp.rows=j.rows;renderMap()}catch(e){toast(e.message,'err')}});
  $$('details.srcv',root).forEach(d=>d.addEventListener('toggle',()=>{S.open[d.dataset.k]=d.open}));
  $('#pgTitle').oninput=e=>{f.pageTitle=e.target.value};
  $('#bGen').onclick=generate;$('#bPrev').onclick=previewFile;
  $('#bCfg').onclick=async()=>{try{const j=await api('/api/generate_batch',{items:[{sid:f.sid,plan,page_title:f.pageTitle??f.doc.page_name}],template_name:S.tplName});dl('mapping-config.json',JSON.stringify(j.results[0].config,null,2));toast('Mapping config downloaded','ok')}catch(e){toast(e.message,'err')}};
  if(multi)$('#bCopy').onclick=async()=>{const targets=okFiles().filter(x=>x!==f).map(x=>x.sid);
    try{const j=await api('/api/copy_plan',{plan,targets});S.files.forEach(x=>{if(j.plans[x.sid])x.plan=j.plans[x.sid]});toast('Mapping copied to '+targets.length+' file(s). Differing layouts fall back to auto-suggest — review each file.','ok',6500)}catch(e){toast(e.message,'err')}};
})}

/* ---------- generate / preview ---------- */
function itemFor(f){return {sid:f.sid,name:f.name,plan:f.plan,page_title:f.pageTitle??f.doc.page_name}}
async function generate(){
  busy(true,'Generating '+okFiles().length+' file(s)…');
  try{const body={template_name:S.tplName,items:okFiles().map(itemFor)};if(S.cfg)body.config=S.cfg;
    S.results=await api('/api/generate_batch',body);S.results.results.forEach(r=>{if(r.sid)S.previews[r.sid]=r});
    const good=S.results.results.filter(r=>!r.failed&&r.ok).length;toast(good+' of '+S.results.results.length+' passed validation',good===S.results.results.length?'ok':'warn');go('res');
  }catch(e){toast(e.message,'err',7000)}finally{busy(false)}}
async function previewFile(){
  const f=F();busy(true,'Building preview…');
  try{const body={template_name:S.tplName,items:[itemFor(f)]};if(S.cfg)body.config=S.cfg;
    const j=await api('/api/generate_batch',body);S.previews[f.sid]=j.results[0];go('prev');
  }catch(e){toast(e.message,'err',7000)}finally{busy(false)}}

/* ---------- 3. preview ---------- */
function safeHtml(s){const t=document.createElement('template');t.innerHTML=s||'';
  const ok=new Set(['P','UL','OL','LI','STRONG','B','EM','I','SPAN','H1','H2','H3','H4','H5','H6','DIV']);
  const go=n=>{let o='';n.childNodes.forEach(c=>{if(c.nodeType===3)o+=esc(c.textContent);else if(c.nodeType===1){const g=c.tagName;
    if(g==='SCRIPT'||g==='STYLE')return;if(g==='BR'){o+='<br>';return}const inner=go(c);o+=ok.has(g)?'<'+g.toLowerCase()+'>'+inner+'</'+g.toLowerCase()+'>':inner}});return o};
  return go(t.content)}
const pvCls=n=>n.clone?'cl':(n.written.length?'new':'keep');
function pvNode(n){
  if(n.el!=='widget'){const row=n.dir==='row'||n.dir==='row-reverse';return `<div class="pvct${n.group?' pvgrid':(row?' pvrow':'')}">${n.kids.map(pvNode).join('')}</div>`}
  const f=n.f||{};let b='';
  switch(n.w){
    case 'heading':b=`<div class="pvh ${esc(f.tag||'h2')}">${safeHtml(f.title)}</div>`;break;
    case 'text-editor':b=`<div class="pvtxt">${safeHtml(f.editor)}</div>`;break;
    case 'button':b=`<span class="pvbtn">${esc(f.text)}</span>`;break;
    case 'call-to-action':b=`<div class="pvcard"><b>${esc(f.title)}</b><div>${esc(f.description)}</div>${f.button?`<span class="pvbtn">${esc(f.button)}</span>`:''}</div>`;break;
    case 'image-box':b=`<div class="pvcard"><b>${esc(f.title_text)}</b><div>${esc(f.description_text)}</div></div>`;break;
    case 'image':b=`<div class="pvimg">🖼 ${esc((f.url||'(no image)').split('/').pop())}</div>`;break;
    case 'shortcode':b=`<code>${esc(f.shortcode)}</code>`;break;
    case 'template':b=`<div class="pvimg">Global Elementor template #${esc(f.template_id)} — content lives outside this JSON</div>`;break;
    case 'nested-accordion':b=(f.items||[]).map(it=>`<div class="pvacc${it.clone?' cl':''}"><b>${esc(it.title)}</b><div class="pvtxt">${safeHtml(it.answer)}</div></div>`).join('');break;
    default:b='<div class="mut">(widget not drawn in preview)</div>'}
  return `<div class="pvw ${pvCls(n)}"><div class="pvchip"><b>${esc(n.w)}</b> #${esc(n.id)}${n.written.length?' · filled: '+esc(n.written.join(', ')):' · template default'}${n.clone?' · cloned (new)':''}</div>${b}</div>`}
function secLabel(sc,P){const h=(function f(n){if(n.el==='widget')return n.w==='heading'&&n.f?n.f.title.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim():null;for(const k of n.kids){const r=f(k);if(r)return r}return null})(sc.node);return h||'Section '+sc.index}
function renderPrev(){keepScroll(()=>{
  const root=$('#v_prev'),f=F(),r=f&&S.previews[f.sid];let h=fileBar();
  if(r&&r.failed){root.innerHTML=h+`<div class="card pad err">Preview failed: ${esc(r.failed)}</div>`;bindFileBar(root);return}
  if(!r){root.innerHTML=h+'<div class="card empty"><div style="font-size:30px">👁</div><p>No preview yet for this file.</p><button class="btn" id="bPrev">Build preview</button></div>';bindFileBar(root);$('#bPrev').onclick=previewFile;return}
  const P=r.preview,c=P.counts;
  h+=`<div class="card pad"><div class="row"><div><h2 style="margin:0">Section preview</h2><span class="mut">${esc(f.name)}</span></div><span class="sp"></span><label class="row"><input type="checkbox" id="pvDim"> highlight only added content</label><button class="btn sec sm" id="bPrev">Rebuild</button></div>
   <div style="margin-top:10px"><span class="lg"><i style="background:var(--ok)"></i>filled from your content (${c.new})</span><span class="lg"><i style="background:var(--warn)"></i>cloned / extra item (${c.cloned})</span><span class="lg"><i style="background:#9aa3b2"></i>template default (${c.keep})</span></div>
   <div class="mut" style="margin-top:4px">“from Content N” = the Nth block of your Word file (counted from 0); “no content — template as-is” = nothing from your file was placed here, so the template’s original text is still there. Basic wireframe, not Elementor’s styling. Each block shows the widget type, its id and the fields that were filled.</div></div>`;
  h+='<div class="pvgrid2"><aside class="card toc" aria-label="Sections">'+P.sections.map(sc=>`<a data-t="${sc.index}"><span class="num" style="width:24px;height:24px;font-size:12px">${sc.index}</span><span style="min-width:0"><span style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(secLabel(sc,P).slice(0,40))}</span><small>${sc.sources.length?'from Content '+sc.sources.join(', ')+' · '+esc((P.source_titles[sc.sources[0]]||'').slice(0,24)):(sc.derived?'from the document title':'no content — template as-is')}</small></span></a>`).join('')+'</aside><div id="pvRoot">';
  P.sections.forEach(sc=>{const src=sc.sources.length?sc.sources.map(i=>`<span class="chip acc">Content ${i} ${esc((P.source_titles[i]||'').slice(0,50))}</span>`).join(' '):(sc.derived?'<span class="chip">derived from the document title</span>':'<span class="chip">no content mapped — template as-is</span>');
    h+=`<div class="card pad pvsec" id="pvs${sc.index}"><div class="row" style="margin-bottom:8px"><span class="num">${sc.index}</span><b>Template section ${sc.index}</b><code class="mut">#${esc(sc.node.id)}</code><span class="sp"></span>${src}</div>${pvNode(sc.node)}</div>`});
  h+='</div></div>';
  if(P.unplaced.length||P.ignored.length){h+='<div class="card pad"><h2>Content sections not shown above</h2>'+P.unplaced.map(u=>`<div><span class="chip warn">not placed</span> Content ${u.index} ${esc(u.title)}</div>`).join('')+P.ignored.map(u=>`<div class="mut"><span class="chip">ignored</span> Content ${u.index} ${esc(u.title)} — ${esc(u.reason)}</div>`).join('')+'</div>'}
  root.innerHTML=h;bindFileBar(root);
  $('#pvDim').onchange=e=>$('#pvRoot').classList.toggle('dimkeep',e.target.checked);
  $('#bPrev').onclick=previewFile;
  $$('.toc a',root).forEach(a=>a.onclick=()=>{const el=document.getElementById('pvs'+a.dataset.t);if(el)el.scrollIntoView({behavior:'smooth',block:'start'})});
})}

/* ---------- 4. results ---------- */
function detail(r){
  const sec=(t,b)=>`<h3>${t}</h3>${b}`;let h='';
  if(r.errors.length)h+=sec('<span class="err">Errors</span>','<ul>'+r.errors.map(e=>'<li>'+esc(e)+'</li>').join('')+'</ul>');
  h+=sec('Warnings &amp; ambiguities ('+r.warnings.length+')',r.warnings.length?'<ul>'+r.warnings.map(e=>'<li>'+esc(e)+'</li>').join('')+'</ul>':'<span class="mut">None</span>');
  h+=sec('Unmatched source content',(!r.unmapped_sections.length&&!r.unmapped_nodes.length)?'<span class="mut">None</span>':
    r.unmapped_sections.map(s=>`<details><summary><b>Content ${s.index}</b> not mapped anywhere</summary><pre>${s.text.map(esc).join('\n')}</pre></details>`).join('')+r.unmapped_nodes.map(n=>`<div>Content ${n.section} ${esc(n.kind)}: ${esc(n.text)}</div>`).join(''));
  h+=sec('Mapping summary',`<div class="tbl-wrap"><table><tr><th>Content </th><th>Source</th><th>→ Template</th><th>Field</th><th>Status</th></tr>${r.mapping.map(m=>`<tr><td>${m.section??'–'}</td><td>${esc(m.source)}</td><td><code>${esc(m.target)}</code> ${esc(m.widget)}</td><td>${esc(m.field)}</td><td>${esc(m.status)}</td></tr>`).join('')}</table></div>`);
  h+=sec('Template fields kept (no source value)',`<div class="tbl-wrap"><table><tr><th>Element</th><th>Value</th><th>Why</th></tr>${r.retained.map(x=>`<tr><td><code>${esc(x.id)}</code> ${esc(x.widget+'.'+x.field)}</td><td>${esc(x.value)}${x.stale.length?` <span class="chip warn">stale: ${esc(x.stale.join(', '))}</span>`:''}</td><td class="mut">${esc(x.reason)}</td></tr>`).join('')}</table></div>`);
  h+=sec('Media kept from template','<ul>'+r.media.map(m=>`<li><code>${esc(m.id)}</code> ${esc(m.widget)} — <span class="mut">${esc(m.url)}</span>${m.stale.length?` <span class="chip warn">${esc(m.stale.join(', '))}</span>`:''}</li>`).join('')+'</ul>');
  h+=sec('Validation checks','<ul>'+r.checks.map(k=>`<li>${k.ok?'<span class="ok">✔</span>':'<span class="err">✘</span>'} ${esc(k.check)}${k.detail?` <span class="mut">— ${esc(k.detail)}</span>`:''}</li>`).join('')+'</ul>');
  return h}
function renderRes(){keepScroll(()=>{
  const root=$('#v_res');if(!S.results){root.innerHTML='<div class="card empty">Nothing generated yet.</div>';return}
  const R=S.results.results,good=R.filter(r=>!r.failed&&r.ok).length,sum=k=>R.reduce((a,r)=>a+(r.counts?r.counts[k]:0),0),um=R.reduce((a,r)=>a+(r.unmapped_sections?r.unmapped_sections.length:0),0);
  let h=`<div class="row" style="margin-bottom:14px"><div><h1 style="font-size:20px;margin:0">${good} of ${R.length} file(s) passed validation</h1><span class="mut">Valid JSON, template structure preserved, source text verified.</span></div><span class="sp"></span><button class="btn" id="dZip">⬇ Download all (.zip)</button></div>`;
  h+=`<div class="tiles"><div class="card tile"><b class="${good===R.length?'ok':'warn'}">${good}/${R.length}</b><span>files passed</span></div><div class="card tile"><b>${sum('written')}</b><span>fields written</span></div><div class="card tile"><b>${sum('clones')}</b><span>elements cloned</span></div><div class="card tile"><b class="${sum('warnings')?'warn':''}">${sum('warnings')}</b><span>warnings to review</span></div><div class="card tile"><b class="${um?'warn':''}">${um}</b><span>unplaced sections</span></div></div>`;
  h+='<div class="card"><div class="tbl-wrap"><table><tr><th>File</th><th>Status</th><th>Written</th><th>Cloned</th><th>Warnings</th><th>Unplaced</th><th>Download</th></tr>';
  R.forEach((r,i)=>{
    if(r.failed){h+=`<tr><td>${esc(r.name)}</td><td colspan="6"><span class="chip err">failed</span> ${esc(r.failed)}</td></tr>`;return}
    h+=`<tr><td><b>${esc(r.name)}</b><br><span class="mut mono">${esc(r.stem)}.json</span></td><td>${r.ok?'<span class="chip ok">passed</span>':`<span class="chip err">failed (${r.counts.errors})</span>`}</td><td>${r.counts.written}</td><td>${r.counts.clones}</td><td>${r.counts.warnings?`<span class="chip warn">${r.counts.warnings}</span>`:'0'}</td><td>${r.unmapped_sections.length}</td>
     <td><div class="row" style="gap:6px"><button class="btn sm dj" data-i="${i}">JSON</button><button class="btn sm sec dr" data-i="${i}">Report</button><button class="btn sm sec dc" data-i="${i}">Config</button><button class="btn sm sec dp" data-i="${i}">Preview</button></div></td></tr>
     <tr><td colspan="7" style="padding:0"><details><summary class="mut" style="padding:8px 10px">Details — warnings, unmatched content, mapping, validation</summary><div class="det">${detail(r)}</div></details></td></tr>`});
  root.innerHTML=h+'</table></div></div>';
  $('#dZip').onclick=()=>{dlBlob('mapped-json-files.zip',b64Blob(S.results.zip_b64,'application/zip'));toast('ZIP downloaded: one folder per file (JSON, report, mapping)','ok')};
  $$('.dj',root).forEach(b=>b.onclick=()=>{const r=R[+b.dataset.i];dl(r.stem+'.json',JSON.stringify(r.output,null,2))});
  $$('.dr',root).forEach(b=>b.onclick=()=>{const r=R[+b.dataset.i];dl(r.stem+'.report.md',r.report_md,'text/markdown')});
  $$('.dc',root).forEach(b=>b.onclick=()=>{const r=R[+b.dataset.i];dl(r.stem+'.mapping.json',JSON.stringify(r.config,null,2))});
  $$('.dp',root).forEach(b=>b.onclick=()=>{const r=R[+b.dataset.i],i=S.files.findIndex(f=>f.sid===r.sid);if(i>=0)S.cur=i;go('prev')});
})}
renderUp();renderSteps();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    url = f"http://127.0.0.1:{a.port}"
    print(f"Content -> JSON Mapper running at {url}  (Ctrl+C to stop)")
    if not a.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
