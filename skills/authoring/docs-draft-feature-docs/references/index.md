# Area registry

`docs-draft-feature-docs` checks this file in Step 2, after the baseline is loaded and before drafting.

Resolve in this order. Stop at the first hit **for a single-area request** — but a request can span areas, and several rows below name the seams where that happens. When it does, load every file that owns a piece of the request and say which half went where.

## 1. Specialist skills — delegate and stop

These areas already have a dedicated drafting skill. Hand off and do not draft a second opinion.

| Area | Delegate to | Scope |
|---|---|---|
| Lens charts | `docs-lens-chart-page` | Individual chart type pages. Pairs with `docs-lens-chart-settings` for verifying UI labels |
| Cases | `docs-draft-cases-docs` | Migration in progress — see [`status.md`](status.md#cases-specialist-migration). That skill is **not in this catalog**, so check it is installed rather than assuming |

`docs-lens-chart-page` runs `context: fork`, so it returns a result rather than a running conversation. **Confirm a specialist is actually installed before routing to it** — a delegation to a skill that is not on the machine fails, and deriving from the area file or sibling pages is better than stopping.

This table is transitional, and Workflows has already made the trip: its area knowledge moved into `workflows.md` and its row moved down. Do the same for any remaining specialist whose value is facts rather than process. Until then, delegation wins for the rows above — a specialist that is installed and tested beats a generic draft.

## 2. Area files — load and apply

| Area | File | Notes |
|---|---|---|
| Elastic Security | `elastic-security.md` | Narrative under `solutions/security/`, reference under `reference/security/`, rule content in another repo again. Mid-restructure |
| Alerting and Cases | `alerting-and-cases.md` | Platform capabilities the solutions also surface, so placement is the main risk. Mid-GA-transition |
| Elastic Workflows | `workflows.md` | Step references, triggers, authoring techniques. Migrated from the `docs-draft-workflow-docs` skill. Meets `alerting-and-cases.md` at triggers |
| Kibana settings reference | `kibana-settings-reference.md` | **Not in docs-content.** These pages publish from `elastic/kibana`, and the content is settings YAML rather than prose. Read the file before assuming `$DOCS_CONTENT_ROOT` is the working tree |
| Elastic Agent Builder | `agent-builder.md` | Agents, skills, tools, MCP and A2A servers. Split from `ai-features.md` on size |
| AI-powered features | `ai-features.md` | The hub, the AI assistants, LLM connector guides, Automatic Import. **Placement is a three-way platform-or-solution decision** and the three assistants are separate plugins. Meets `elastic-security.md` |

An area file whose frontmatter carries a `status:` key has an in-flight transition affecting it. Read that entry in [`status.md`](status.md) and resolve its tracking issues before drafting — do not take this table's word for what is in flight, because a row here is one more place to forget.

Use `search_docs` on the feature name when the area is not obvious from the request. The published navigation context it returns names the area faster than reading this table does.

An area file **adds** facts and narrows choices. It can never override the style guide, content types, cumulative-docs rules, or the approval gates. When an area file appears to contradict the baseline, follow the baseline and flag the conflict.

## 3. Neither — derive and say so

Continue with the baseline alone. Derive conventions from sibling pages, which `find_related_docs` will give you, and state in the output that no area file existed so the next person knows what to add.

## Adding an area

1. Copy `_template.md` to `<area-name>.md`, named for the docs area rather than the engineering team, since teams get reorganized and directories mostly do not.
2. Fill the frontmatter and the five headings. Verify every path and label before it goes in, because this file becomes a source of truth for everyone who drafts here, and record the date in `verified:`.
3. Add the row above, and name any area it shares a seam with. Add the reciprocal line to that area's file too, so the seam is visible from both sides.
4. Anything with a shelf life goes in [`status.md`](status.md) instead, with an expiry condition. Add `status:` to the area file's frontmatter so a reader is sent there.

**If `search_docs` can answer it, leave it out.** Page inventories and file counts are maintenance work that buys nothing — the MCP already knows every published page, and it stays current. An area file records what the MCP cannot know: the boundary, the product source paths that settle a fact, the local conventions, the navigation file, and the traps. Length follows from how much of that the area has, so aim for signal rather than a line count.

`_template.md` has the full set of rules for keeping an area file from going stale — expiry conditions over dates, grep targets alongside paths, checks rather than snapshots, and substitutions rather than literal product names.
