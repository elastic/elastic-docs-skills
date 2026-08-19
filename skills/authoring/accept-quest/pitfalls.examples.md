# Documentation pitfalls

Starter checklist shipped with `docs-accept-quest`. Copy this file (or point the skill at your existing pitfalls file) during first-run setup. Scan the diff against the entries whose **When** line matches.

**In scope:** mistakes visible in the doc artifact itself (grep the docs corpus, read the diff structure, compare prose to screenshots).

**Out of scope:** product source verification (defaults, i18n, route config, lifecycle in code). Run that once upstream in your authoring or review workflow — do not duplicate it here.

## How to use

1. Skim the diff.
2. For each entry below, if **When** matches, run **Check**.
3. Fix anything that fails before you request review.

## Entry format

Each pitfall has an id, a **When** trigger, and a **Check** you can run on the diff or docs corpus.

---

## Structure and procedures

### PIT-DOC-01: Contradictory lifecycle badges on one entry

- **When:** `applies_to` sets both `stack` and deployment keys (`ech`, `ece`, `eck`, `self`) that would render incompatible lifecycles on the same setting or section (for example `stack: experimental` with `ech: ga`)
- **Check:** Read all keys on the entry together. Align stack and deployment lifecycles, or split the content if lifecycles genuinely differ.

### PIT-DOC-02: Single-step numbered procedure

- **When:** a numbered procedure (`1.` …) has only one step
- **Check:** Split into at least two genuine action steps, or convert to prose. Never pad with a result-only step ("The file downloads").

### PIT-DOC-03: Independent actions numbered as sequential steps

- **When:** numbered steps list optional, reorderable, or independent actions after the main task completes
- **Check:** Keep the numbered spine for actions that must happen in sequence. Move independent post-result actions to an unnumbered option list.

### PIT-DOC-04: Issue or PR wording copied into user docs

- **When:** prose copied from an issue's suggested edits, a PR description, or a PR title — especially internal mechanism ("internally converting", handler names) or unverified UI strings
- **Check:** Cut mechanism detail the reader cannot see or act on. Replace every UI label with the string verified in product source, not the issue or PR wording.

### PIT-DOC-05: Prose or alt text mismatches the screenshot

- **When:** prose or image alt text describes a field, control, or value shown in an adjacent screenshot
- **Check:** Confirm the text matches what the image shows. Fix prose and alt text to match the image, or flag the screenshot for refresh.

---

## Links and references

### PIT-DOC-06: API or product link not used elsewhere in the corpus

- **When:** the diff adds a product or API URL that does not appear in existing docs or cross-links
- **Check:** Search the docs for how that API or page is already linked. Do not rely on HTTP 200 alone (SPAs return 200 for invalid paths). Reuse the established target.

### PIT-DOC-07: Sample-data prerequisite linked to a generic landing page

- **When:** a sample-data prerequisite points at a broad Explore and analyze (or similar) anchor instead of the sample-data page
- **Check:** Link to the dedicated sample-data page (`manage-data/ingest/sample-data.md` in docs-content).

### PIT-DOC-08: Sample-data time range stated as always correct

- **When:** sample-data examples use a fixed time range (for example **Last 7 days**) without qualification
- **Check:** State that sample-data timestamps are relative to when the data set was installed. Name **Last 7 days** only as valid when the set was just installed.

---

## Terminology and UI copy

### PIT-UI-01: Non-canonical product or feature name

- **When:** the diff introduces a product, feature, or architecture term that differs from established docs usage without justification
- **Check:** Search the corpus for the canonical term (for example Elastic Inference Service, not "{{kib}} inference service"; **time filter**, not time picker). Do not invent variants unless the diff explains why the standard term does not apply.

### PIT-UI-02: Developer vocabulary in user-facing prose

- **When:** prose names a UI control using package names, component names, PR titles, test IDs, or aria-labels
- **Check:** Search sibling docs for the established user-facing term before naming the control.

### PIT-UI-03: Wrong product or API name

- **When:** the diff uses a non-corpus product or API name (for example "Dashboard API" instead of **Dashboards API**)
- **Check:** Search the corpus for the established name before introducing a variant.

### PIT-UI-04: "Control" used for a non-dashboard-control element

- **When:** prose uses **control** for a toggle, option, button, or menu item that is not a dashboard control
- **Check:** Reserve **control** for dashboard controls. Use **option**, **toggle**, or the specific UI element name otherwise.

### PIT-UI-05: Internal scope term in running prose

- **When:** prose uses **global** or similar internal scope vocabulary outside a literal UI label quote
- **Check:** Name the concrete scope instead ("dashboard filters", "the dashboard query"). Use **global** only when quoting the UI label verbatim.
