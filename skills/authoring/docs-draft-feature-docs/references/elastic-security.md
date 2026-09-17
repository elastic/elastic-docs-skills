# Elastic Security

The Security solution: detections and alerts, investigation tools, Elastic Defend and endpoint response, entity analytics, cloud security, and the AI features inside Security.

The boundary that matters: Security owns the **narrative** under `solutions/security/`, but its **reference** material lives under `reference/security/`, and anything about the underlying Elasticsearch or Kibana platform belongs to those areas instead. Detection rule *content* is a third place again — see *Known traps*.

> **Recheck paths against the repo while the Security restructure is in flight.** Verified against `docs-content`, `kibana`, and `detection-rules` on 2026-09-16. The docset is being restructured around reader posture under [docs-content-internal#1541](https://github.com/elastic/docs-content-internal/issues/1541), shipping as a stack of pull requests with a deadline of 2026-10-31. Most of the change regroups `toc.yml` and keeps paths, but a few directories actually move — those are the ones whose pull requests need redirects. Mid-stack the repo is half-moved, so use `search_docs` and the local tree rather than any path written here, and refresh the *Navigation* and *Known traps* sections once the stack has merged.
>
> Also update in that pass: the Elastic Security row in `index.md`, and the eval asserting that navigation lives in `solutions/toc.yml` with no per-solution toc, which holds only if the new wrapper sections do not adopt nested sub-tocs.

## What belongs here, and what does not

| The content is | Home |
|---|---|
| Setting up a Defend policy | `configure-elastic-defend/`. Operating it afterward is `manage-elastic-defend/` — a genuine split, and guessing produces a page that is hard to find |
| A long field, setting, or command table | `reference/security/`, not a narrative page under `solutions/security/`. This is a common review comment |
| Detection rule content itself | The `elastic/detection-rules` repo. "Document a new rule" usually means no docs-content page at all |
| An AI feature inside Security | Here, but **load `ai-features.md` alongside this file** — it owns the platform-or-solution placement rule, and `agent-builder.md` owns the Agent Builder pages |

`solutions/security/cloud/_snippets/` is the only snippets directory in the area, so shared prose elsewhere in Security is currently duplicated rather than included. Check it before writing anything about cloud security, and do not assume an include exists for anything else.

## Source of truth

Kibana's Security plugin is at `x-pack/solutions/security/plugins/security_solution/` — note the `x-pack/solutions/` prefix, not the older `x-pack/plugins/` path that stale docs and search results still point at.

| Question | Verify at |
|---|---|
| UI labels and strings | `public/<feature>/**/translations.ts`, plus inline `i18n.translate` calls under `public/`. The subdirectories are named by feature: `detection_engine`, `entity_analytics`, `exceptions`, `flyout`, `attack_discovery`, `cloud_security_posture`, and so on |
| Settings and defaults | `server/config.ts` for plugin config. Defend policy defaults live under `server/endpoint/` |
| API request and response shapes | `common/api/`, for example `common/api/detection_engine/` |
| Prebuilt rule packaging and upgrades | `server/lib/detection_engine/prebuilt_rules/` |
| Detection rule content | The `elastic/detection-rules` repo, **not** Kibana. `rules/` is organized by platform, and hunting queries are in `hunting/` |

Endpoint agent internals are not in a public repo. When a claim depends on them, it is an open question for the Defend team rather than something to verify yourself.

## Conventions

Frontmatter on a typical Security page carries `mapped_pages` with both legacy URLs, `applies_to` covering stack and serverless Security, `products`, and a `description`:

```yaml
mapped_pages:
  - https://www.elastic.co/guide/en/security/current/<page>.html
  - https://www.elastic.co/guide/en/serverless/current/security-<page>.html
applies_to:
  stack: ga
  serverless:
    security: ga
products:
  - id: security
  - id: cloud-serverless
description: <one sentence, active, naming the reader's task>
```

New pages have no legacy equivalent, so they get **no** `mapped_pages`. Never invent one. The serverless key is nested under `serverless:` as `security:`, not written flat.

Use the substitutions rather than typing product names: `{{elastic-sec}}`, `{{elastic-defend}}`, `{{elastic-endpoint}}`, `{{ml-cap}}` for Machine learning, and `{{serverless-short}}`.

Headings carry explicit anchor IDs in brackets, on the H1 and on section headings — `# Suppress detection alerts [security-alert-suppression]`. Existing anchors preserve legacy deep links, so never change or remove one on an existing page. New headings get a new stable slug.

Feature prerequisites go in a `::::{admonition} Requirements` block near the top, not scattered through the page.

Model pages: `detect-and-alert/alert-suppression.md` for a feature page, with a lead paragraph that states the problem before the feature and a Requirements block covering subscription and ML prerequisites; and `detect-and-alert/choose-the-right-rule-type.md` for a decision page, which opens by naming the reader's question and answers it with a comparison table ordered as a decision flow.

## Navigation

`solutions/toc.yml` holds the whole Security tree inline, starting at the `- file: security.md` entry. There is **no** `solutions/security/toc.yml`, and adding one will not work, because `docset.yml` maps the `solutions` toc as one unit. `reference/security/` is the exception and has its own `toc.yml`.

Add the page to its parent's `children:` list in the position it should appear, since order in the file is the order in the sidebar. Then link it from the subdirectory's landing page. That landing page is normally a **sibling** of the directory rather than an `index.md` inside it — `detect-and-alert.md` sits next to `detect-and-alert/` — but the pattern is not universal, so check the actual directory instead of assuming either shape.

## Known traps

- **Defend, Endpoint, and detection rules are three different things.** {{elastic-defend}} is the integration users configure, {{elastic-endpoint}} is the agent component, and detection rules are content shipped from `detection-rules`. Requests conflate them constantly. Establish which one the change touches before choosing a directory.
- **Detection rule content is not documented in docs-content.** Confirm before drafting a page that should not exist.
- **Serverless Security has product tiers, and there is no frontmatter field for them.** Tier requirements such as Security Complete are written in prose, typically in the Requirements admonition. Do not invent a `product_tier` key.
- **The Kibana plugin moved.** Paths under `x-pack/plugins/security_solution/` are stale. Verifying against a stale path silently finds nothing and looks like a missing feature.
