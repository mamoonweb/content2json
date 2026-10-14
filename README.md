# content_to_json

## Easiest way: the web UI (one or many content files)
    pip install python-docx
    python ui.py                 # opens http://127.0.0.1:8765  (use --port / --no-browser if needed)

The page is a 4-step flow (top bar): **Files → Mapping → Preview → Results**. Light/dark toggle at the top right.
1. **Files** - drag & drop (or click) one or many .docx files, the Elementor template .json, and optionally a saved mapping config.
   Files appear as removable chips; **Analyze** unlocks once a .docx and a template are present. Unreadable files are flagged and skipped.
2. **Mapping** - each file has its own auto-suggested mapping (switch with the file pills).
   - A summary strip shows how many template sections are filled and how many content sections are not placed.
   - Every template section card shows its widget types, a "Fill from" dropdown, and one dropdown per widget field.
     "Source content" under a card shows exactly what the chosen content section contains.
   - Tick content sections that are header/menu/footer to ignore them.
   - The bottom bar (always visible): page title, *Copy mapping to other files*, *Download mapping*, *Preview this file*, *Generate*.
3. **Preview** - every template section as a basic wireframe with a section navigator on the left. Each block is labelled with its
   Elementor widget type + id and the fields filled. Green = filled from content, orange = cloned extra item, grey = template default.
4. **Results** - stat tiles, per-file status, JSON / Report / Config / Preview buttons per file, a details panel (warnings, unmatched
   content, mapping table, kept template fields, validation checks) and **Download all (.zip)** (one folder per file).

A saved mapping config uploaded in step 1 is applied to every file (page title stays per file, derived from each document title).
Everything runs locally; the files never leave your machine.

## Command line

Maps a Word content file (.docx) onto an Elementor JSON template. The engine has no page-specific
logic; everything page-specific lives in a mapping config (JSON).

    pip install python-docx
    python content_to_json.py inspect --content page.docx --template tpl.json      # see sections + template widget ids
    python content_to_json.py map --content page.docx --template tpl.json \
        --mapping mapping.albert-services-electrical.json --out out.json --report report.md [--strict]

Exit code 1 on any validation error (and, with --strict, on any warning / unmapped content).

## How a content file is read
Each top-level table (or loose paragraph) = one *section*. Inside a section, nested tables are
flattened in reading order and each paragraph is classified:
placeholder (`*Insert ...*`, `Insert Image`) · heading (Word Heading N) · list item (`· x`) ·
button (bold, <= `button_max_words` words, or `[x]`, or ends with " Button") · label (long bold) · paragraph.
Per section the tool derives: `title` (first heading), `paras` (text between title and first card),
`cards` (headings deeper than the title, each with its body/button, scoped to the same table cell),
`buttons` (outside cards), `items`, `outro`.

## Mapping config
- `ignore`: sections that are not page content (header / nav / footer), with a reason.
- `vars` / `page`: values derived from the document title by regex (reported as DERIVED).
- `rules[].section`: `{"index": n}` or `{"title_regex": "..."}`, plus `expect` (e.g. `{"cards": ">=6"}`) -> STRUCTURE DRIFT warning if the layout differs.
- `rules[].binds`:
  - simple: `{"target": <elementor id>, "field": <settings key>, "value": "title|paras|buttons[0]|..."}`; optional `"as"`, `"span_last_words"`, or `"compose"` (paragraphs + list of cards)
  - `repeat`: fill a container's child widgets from `cards`/`buttons`; extra items clone the slot (`clone_from`), logged + warned
  - `accordion`: nested-accordion items + child containers from cards
- `retain`: documents template fields intentionally kept (shown in the report).

## Guarantees checked on every run
valid JSON · same top-level keys/version/type · every original element id still present with same elType/widgetType,
settings keys and value types, parent and order · new ids only from logged clones · unique ids · accordion items == containers ·
no source node mapped to two targets · no (target, field) written twice · every mapped text found verbatim in its field ·
no unmapped section/node without being reported · no stale template terms (derived from the old page title) in retained text/media.

## Not done by design
No values are invented. Image placeholders, contact form, phone number, header/nav/footer and sections with no template
counterpart are reported, never guessed. New keys are never added to existing widgets.
