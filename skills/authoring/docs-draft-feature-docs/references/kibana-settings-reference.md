# Kibana settings reference

The Kibana advanced settings and `kibana.yml` configuration reference, published at `elastic.co/docs/reference/kibana/`.

**This area is not in docs-content.** It lives in the `elastic/kibana` repo under `docs/`, which has its own `docset.yml`, `toc.yml`, and `redirects.yml`. So `$DOCS_CONTENT_ROOT` is the wrong working tree here, and you need `$KIBANA_ROOT` to write, not only to verify. Confirm that before drafting, because the published URL path `reference/kibana/...` looks like docs-content and is not.

The boundary that matters: this area owns **settings metadata** — what a setting is, its datatype, default, and availability. How to accomplish a task using a setting is narrative content and belongs in docs-content. When both are in play, the settings entry is the canonical home for the metadata and the narrative page links to it.

> Verified against `elastic/kibana` on 2026-09-16. Scoped to the advanced settings pages and `docs/reference/configuration-reference/`. The rest of the Kibana repo's `docs/reference/` tree — connectors, audit events, commands, plugins, user activity, cloud — is out of scope and would need its own file. The repo-level facts below apply to all of it, so promote them to a shared file if a second Kibana-repo area appears.

## What belongs here, and what does not

You almost never edit the Markdown. Each page is a thin shell that renders one or more YAML data files through the `:::{settings}` directive, which takes a path rooted at the docset with a leading slash: `:::{settings} /reference/configuration-reference/cases-settings.yml`. **The content is the YAML.**

| The content is | Home |
|---|---|
| A new or changed setting | The YAML file the owning page renders. Read the shell to find which file, rather than inferring it from the filename |
| Intro prose, required permissions, how to reach the UI | The `.md` shell |
| How to accomplish a task with a setting | docs-content, linking here for the metadata |

Advanced settings and `kibana.yml` settings are different things. Advanced settings are changed in the Kibana UI under **Advanced Settings**; configuration-reference settings are changed in `kibana.yml`. A request naming a setting does not always say which, and they live in different files.

Advanced settings split again by scope, into a space-level file and a global file. **Scope is a property of the setting's registration, not something to infer.** Read the `uiSettings` registration to find which one, and never pick a file by which is larger or busier.

Shell-to-YAML pairing is usually one-to-one but is not guaranteed. `reporting-settings.md` renders five YAML files, none of which has an `.md` of its own, and the advanced settings shell renders two. When a page is split that way, which file a setting belongs in is a real decision.

## Source of truth

| Question | Verify at |
|---|---|
| The settings YAML schema | [docs-builder automated settings reference](https://github.com/elastic/docs-builder/blob/main/docs/syntax/automated_settings.md). The YAML files link it in a header comment |
| Whether a `kibana.yml` setting exists, its default and datatype | The owning plugin's `server/config.ts` in `elastic/kibana`. The schema is the truth, not the current docs entry |
| Whether an advanced setting exists, its UI label, and its scope | The registering plugin's `uiSettings` registration. Search the setting key across `src/` and `x-pack/` |
| Which deployment types a setting reaches | The plugin config and the deployment's own limits. Do not copy `applies_to` from a neighboring setting |

An existing entry is not evidence. These files are hand-maintained rather than generated from the code, so a stale default or a missing setting is exactly the kind of bug this work fixes.

## Conventions

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

`datatype` has no enforced vocabulary and the existing values disagree with each other: `bool` is normal but at least one file uses `boolean`, and lists appear as `array`, `array of strings`, and `list` depending on the file. `float`, `json`, `object`, `enum`, and `image` are also in use. Match the file you are editing, and do not fix a neighbor's spelling as a drive-by.

### Deployment keys, not just stack and serverless

`applies_to` here uses the deployment vocabulary: `stack`, `ech` (Elastic Cloud Hosted), `ece` (Elastic Cloud Enterprise), `eck` (Elastic Cloud on Kubernetes), `self` (self-managed), and `serverless`. Narrative docs-content pages rarely enumerate these, so the habit of writing only `stack` and `serverless` leaves a setting silently unscoped. Page-level frontmatter uses the nested form, as in `applies_to: deployment: self: all`. Let `docs-applies-to-tagging` set the values.

### Order

Settings appear in the order they appear in the file, and the advanced settings page states that it follows the order used in the Kibana UI. **Insert a new setting where the UI puts it**, not alphabetically and not at the end. Group choice matters for the same reason.

### Substitutions and cross-repo links

Both `{{product.kibana}}` and `{{kib}}` are in use across these pages, so matching the neighboring file gives inconsistent answers. Pick the one the file you are editing already uses and stay consistent within it.

Links from here into docs-content use `docs-content://`, as in `docs-content://explore-analyze/find-and-organize/find-apps-and-objects.md`. Links the other direction use `kibana://reference/...`.

Model files: `configuration-reference/cases-settings.yml`, the smallest complete example and the fastest way to see the whole schema; and `advanced-settings-global.yml`, which shows group-level `note:`, per-setting `id:`, and the full deployment key set.

## Navigation

`docs/reference/toc.yml`, with `project: 'Kibana reference'`. Configuration pages are `children:` of `configuration-reference.md`. The order is roughly alphabetical but not reliably so, so place a new page by reading the file. `docs/docset.yml` maps three tocs: `reference`, `release-notes`, and `extend`.

A new setting inside an existing YAML file needs **no** navigation change, which is most of the work in this area. Only a new settings *page* touches `toc.yml`, and that needs both the `.md` shell and the `.yml`.

Redirects for moved pages go in the Kibana repo's own `docs/redirects.yml`, not docs-content's.

## Known traps

- **Do not add prose to the `.md`.** The shell holds the intro and the directive; settings metadata goes in the YAML. A new setting described in the Markdown will not render as a setting and will be missed by anyone reading the rendered list.
- **Do not guess the advanced settings scope.** Space-level and global are separate files, and the registration says which. Guessing puts the entry on the wrong page, where nobody looking for it will find it.
- **Settings work is almost always the first half of a two-repo change.** The narrative page that tells readers to use the setting lives in docs-content, so the Kibana pull request is the one that has to publish first. Step 4e owns the ordering rule; what is specific here is that this area is nearly always the *earlier* half. [docs-content-internal#1807](https://github.com/elastic/docs-content-internal/issues/1807) is a worked example.
- **Duplicate setting keys need a disambiguating `id`.** `hideAnnouncements` exists in both the space and global advanced settings files, which is why the global entry carries `id: hideAnnouncements-global`. Adding a key that already exists elsewhere without an `id` collides.
- **Cross-repo link paths in neighboring files may be stale.** Several Kibana docs files link to a docs-content path that no longer exists and survives only through a `redirects.yml` entry. Copying a link from a neighbor propagates the stale path, so resolve it against the current docs-content tree or with `get_document_by_url`.
- **The header comments lie.** At least one advanced settings file opens by naming a page it does not generate. Trust the `collection:` and `id:` fields over the comment.
- **A setting documented inline on a narrative page is a duplication bug, not a precedent.** The reference entry is the canonical home for datatype, default, and availability, and the narrative page should link to it rather than restate it.
