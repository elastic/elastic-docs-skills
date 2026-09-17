# Kibana settings reference

The Kibana advanced settings and `kibana.yml` configuration reference, published at `elastic.co/docs/reference/kibana/`.

**This area is not in docs-content.** It lives in the `elastic/kibana` repo under `docs/`, which has its own `docset.yml`, `toc.yml`, and `redirects.yml`. So `$DOCS_CONTENT_ROOT` is the wrong working tree here, and you need `$KIBANA_ROOT` to write, not only to verify. Confirm that before drafting; the published URL path `reference/kibana/...` looks like docs-content and is not.

The boundary that matters: this area owns **settings metadata** — what a setting is, its datatype, default, and availability. How to accomplish a task using a setting is narrative content and belongs in docs-content. When both are in play, the settings entry is the canonical home for the metadata and the narrative page links to it.

> Verified against `elastic/kibana` on 2026-09-16. Scoped to `docs/reference/advanced-settings.md` and `docs/reference/configuration-reference/` (25 pages). The rest of the Kibana repo's `docs/reference/` tree — `connectors-kibana/`, `kibana-audit-events.md`, `commands/`, `kibana-plugins.md`, `user-activity/`, `cloud/` — is out of scope and would need its own file. The repo-level facts below apply to all of it, so promote them to a shared file if a second Kibana-repo area appears.

## Where content lives

You almost never edit the Markdown. Each page is a thin shell that renders one or more YAML data files through the `:::{settings}` directive — `cases-settings.md` is 13 lines and `advanced-settings.md` is 47. **The content is the YAML.**

| Path | What belongs here |
|---|---|
| `docs/reference/advanced-settings.md` | The shell for advanced settings: intro, required permissions, and how to reach the UI. Two `:::{settings}` blocks, one per scope |
| `docs/reference/advanced-settings-space.yml` | Space-level advanced settings. 173 settings across about 2,600 lines — the big one |
| `docs/reference/advanced-settings-global.yml` | Global advanced settings. Only 6 settings, so a request that does not name a scope most likely means the space file |
| `docs/reference/configuration-reference/<area>-settings.md` | A shell per `kibana.yml` settings area. 25 of them, including `alerting`, `cases`, `general`, `task-manager`, `security-solution`, `automatic-import` |
| `docs/reference/configuration-reference/<area>-settings*.yml` | The settings themselves |

The directive takes a path rooted at the docset, with a leading slash: `:::{settings} /reference/configuration-reference/cases-settings.yml`.

Pairing is usually one-to-one but is not guaranteed, so read the shell to find the target rather than inferring the filename. `reporting-settings.md` renders five YAML files — `-enable`, `-encryption-key`, `-background-job`, `-png-pdf`, and `-csv` — none of which has an `.md` of its own, and `advanced-settings.md` renders two. When a page is split this way, which file a setting belongs in is a real decision.

Advanced settings and `kibana.yml` settings are different things. Advanced settings are changed in the Kibana UI under **Advanced Settings**; configuration-reference settings are changed in `kibana.yml`. A request naming a setting does not always say which, and they live in different files.

## Source of truth

| Question | Verify at |
|---|---|
| The settings YAML schema | [docs-builder automated settings reference](https://github.com/elastic/docs-builder/blob/main/docs/syntax/automated_settings.md). The YAML files link it in a header comment |
| Whether a `kibana.yml` setting exists, its default and datatype | The owning plugin's `server/config.ts` in `elastic/kibana` — for example `x-pack/platform/plugins/shared/cases/server/`. The schema is the truth, not the current docs entry |
| Whether an advanced setting exists and its UI label | The registering plugin's `uiSettings` registration. Search the setting key across `src/` and `x-pack/` |
| Which deployment types a setting reaches | The plugin config and the deployment's own limits. Do not copy `applies_to` from a neighboring setting |

An existing entry is not evidence. These files are hand-maintained, not generated from the code, so a stale default or a missing setting is exactly the kind of bug this work fixes.

## Read these first

- `docs/reference/configuration-reference/cases-settings.yml` — 43 lines, the smallest complete example. Read it first to see the whole schema at once.
- `docs/reference/advanced-settings-global.yml` — shows `group`-level `note:`, per-setting `id:`, and the full deployment key set.
- `docs/reference/advanced-settings.md` — the model shell page, including two `:::{settings}` blocks and a section-level `applies_to`.

## Local conventions

### Settings YAML shape

```yaml
product: Kibana
collection: Cases settings in Kibana      # the rendered page heading
id: cases-settings                        # ties to the page anchor
page_description: |
  Markdown. Can hold full prose, numbered steps, and cross-repo links.

groups:
  - group: Cases settings                 # display name of the group
    id: cases-settings
    note: "Optional group-level admonition."
    settings:
      - setting: xpack.cases.files.maxSize
        id: maxSize-global                # only when the key appears in more than one file
        description: |
          Markdown. One or more paragraphs.
        datatype: int                     # see the note below — the vocabulary is not enforced
        default: false
        applies_to:
          stack: ga 9.4+
          ech: ga
          ece: ga
          eck: ga
          self: ga
          serverless: unavailable
```

`description` and `page_description` are block scalars holding real Markdown, so links, code spans, and lists work. Keep them in the same voice as any other docs prose — being inside YAML does not lower the bar.

`datatype` has no enforced vocabulary and the existing values disagree with each other: `bool` is normal but `internationalization-settings.yml` uses `boolean`, and lists appear as `array`, `array of strings`, and `list` depending on the file. `float`, `json`, `object`, `enum`, and `image` are also in use. Match the file you are editing, and do not "fix" a neighbor's spelling as a drive-by.

### Deployment keys, not just stack and serverless

`applies_to` here uses the deployment vocabulary: `stack`, `ech` (Elastic Cloud Hosted), `ece` (Elastic Cloud Enterprise), `eck` (Elastic Cloud on Kubernetes), `self` (self-managed), and `serverless`. Narrative docs-content pages rarely enumerate these, so the habit of writing only `stack` and `serverless` leaves a setting silently unscoped. Page-level frontmatter uses the nested form, as in `applies_to: deployment: self: all`. Let `docs-applies-to-tagging` set the values.

### Order

Settings appear in the order they appear in the file, and `advanced-settings.md` states that the page follows the order used in the Kibana UI. **Insert a new setting where the UI puts it, not alphabetically and not at the end.** Group choice matters for the same reason.

### Substitutions and cross-repo links

Both `{{product.kibana}}` and `{{kib}}` are in use across these pages, so matching the neighboring file gives inconsistent answers. Pick the one the file you are editing already uses and stay consistent within it.

Links from here into docs-content use `docs-content://`, as in `docs-content://explore-analyze/find-and-organize/find-apps-and-objects.md`. Links the other direction use `kibana://reference/...`, which over 200 docs-content files already do.

## Navigation

`docs/reference/toc.yml`, with `project: 'Kibana reference'`. Configuration pages are `children:` of `configuration-reference.md`. The order is roughly alphabetical but not reliably so, so place a new page by reading the file. `docs/docset.yml` maps three tocs: `reference`, `release-notes`, and `extend`.

A new setting inside an existing YAML file needs **no** navigation change, which is most of the work in this area. Only a new settings *page* touches `toc.yml`, and it needs both the `.md` shell and the `.yml`.

Redirects for moved pages go in the Kibana repo's own `docs/redirects.yml`, not docs-content's.

## Known traps

- **Do not add prose to the `.md`.** The shell holds the intro and the directive; settings metadata goes in the YAML. A new setting described in the Markdown will not render as a setting and will be missed by anyone reading the rendered list.
- **Settings work is almost always the first half of a two-repo change.** The narrative page that tells readers to use the setting lives in docs-content, so the Kibana pull request is the one that has to publish first. The skill's Step 1e owns the ordering rule; what is specific here is that this area is nearly always the *earlier* half. [docs-content-internal#1807](https://github.com/elastic/docs-content-internal/issues/1807) spells out a worked example.
- **Duplicate setting keys need a disambiguating `id`.** `hideAnnouncements` exists in both the space and global advanced settings files, which is why the global entry carries `id: hideAnnouncements-global`. Adding a key that already exists elsewhere without an `id` collides.
- **Cross-repo link paths in neighboring files may be stale.** Eight Kibana docs files, including `cases-settings.yml`, link to `docs-content://explore-analyze/alerts-cases/cases.md`, which no longer exists — it survives only through a `redirects.yml` entry mapping it to `explore-analyze/cases.md`. Copying a link from a neighbor propagates the stale path. Resolve against the current docs-content tree instead.
- **The header comments lie.** `advanced-settings-global.yml` opens by saying it generates the "Logging settings" page. Trust the `collection:` and `id:` fields over the comment.
- **A setting documented inline on a narrative page is a duplication bug, not a precedent.** The reference entry is the canonical home for datatype, default, and availability; the narrative page should link to it rather than restate it. That is the entire premise of #1807.
