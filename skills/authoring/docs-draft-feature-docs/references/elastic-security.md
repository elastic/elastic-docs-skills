# Elastic Security

Covers the Security solution: detections and alerts, investigation tools, Elastic Defend and endpoint response, entity analytics, cloud security, and the AI features inside Security.

The boundary that matters: Security owns the **narrative** under `solutions/security/`, but its **reference** material lives under `reference/security/`, and anything about the underlying Elasticsearch or Kibana platform belongs to those areas instead. Detection rule *content* is a third place again — see *Known traps*.

> **Refresh this file after the Security restructure.** Verified against `docs-content`, `kibana`, and `detection-rules` on 2026-09-16. The docset is being restructured around reader posture under [docs-content-internal#1541](https://github.com/elastic/docs-content-internal/issues/1541), shipping as a stack of pull requests with a deadline of 2026-10-31.
>
> Until that stack has fully merged, **re-check any path in *Where content lives* against the repo before using it.** The directories that actually move are the ones whose pull requests need redirects — `investigate/`, `esql-for-security/`, `mcp-app/`, and `cloud/`, which splits posture evaluation from runtime protection. The rest are regrouped in `toc.yml` only and keep their paths. During the window the repo is half-moved, so this file will be right about some directories and wrong about others with nothing here to say which.
>
> When the stack has merged, refresh in this order: the path table and the *Navigation* section, which is where the real staleness is; the `investigate.md` entry under *Read these first*, since that page moves; and the *Known traps* section, which should gain the Cloud posture-versus-runtime split, the new in-navigation `Reference` section that collides with the `reference/security/` docset path, and the reserved `Agentic security operations` section whose navigation entry does not exist until its first page ships. *Source of truth* and *Local conventions* are unaffected, because the restructure moves documentation and not product code.
>
> Associated files in this skill to update in the same pass: the Elastic Security row in `index.md`, and eval 10 in `evals/evals.json`, which asserts that navigation lives in `solutions/toc.yml` with no per-solution toc. That claim holds only if the new wrapper sections do not adopt nested sub-tocs. Note also that `security-ia-redirects.yaml`, named in the issue, is illustrative and not a tracked file — do not validate against it.

## Where content lives

| Path | What belongs here |
|---|---|
| `solutions/security/detect-and-alert/` | Detection rules, alerts, exceptions, suppression, rule types. The largest and busiest subdirectory |
| `solutions/security/investigate/` | Timeline and templates, cases, Osquery, session view, notes, indicators of compromise |
| `solutions/security/configure-elastic-defend/`, `manage-elastic-defend/` | Defend policies, artifacts, and lifecycle. Configure versus manage is a real split — respect it |
| `solutions/security/endpoint-response-actions/` | Response actions and the command interface |
| `solutions/security/advanced-entity-analytics/` | Entity risk scoring, anomaly detection, ML job requirements |
| `solutions/security/cloud/` | Cloud security posture, workload protection, asset inventory. Has the area's only `_snippets/` directory |
| `solutions/security/ai/` | AI Assistant, Attack Discovery, and related features |
| `solutions/security/get-started/` | Quickstarts, the UI tour, onboarding, SIEM readiness |
| `solutions/security/integrations/`, `dashboards/`, `esql-for-security/`, `mcp-app/` | As named |
| `reference/security/` | `defend-advanced-settings.md`, `endpoint-command-reference.md`, `fields-and-object-schemas/`. Long lookup tables go here, not in the narrative |

`solutions/security/cloud/_snippets/` is the only snippets directory in the area, so shared prose elsewhere in Security is currently duplicated rather than included. Check it before writing anything about cloud security, and do not assume an include exists for anything else.

## Source of truth

Kibana's Security plugin is at `x-pack/solutions/security/plugins/security_solution/` — note the `x-pack/solutions/` prefix, not the older `x-pack/plugins/` path that older docs and search results still point at.

| Question | Verify at |
|---|---|
| UI labels and strings | `public/<feature>/**/translations.ts`, plus inline `i18n.translate` calls under `public/`. The `public/` subdirectories are named by feature: `detection_engine`, `detections`, `entity_analytics`, `exceptions`, `explore`, `flyout`, `cases`, `attack_discovery`, `asset_inventory`, `assistant`, `cloud_security_posture`, `dashboards` |
| Settings and defaults | `server/config.ts` for plugin config. Defend policy defaults live under `server/endpoint/` |
| API request and response shapes | `common/api/` — for example `common/api/detection_engine/` |
| Prebuilt rule packaging and upgrades | `server/lib/detection_engine/prebuilt_rules/` |
| Detection rule content itself | The `elastic/detection-rules` repo, **not** Kibana. `rules/` is organized by platform: `windows/`, `linux/`, `macos/`, `network/`, `ml/`, `integrations/`, `threat_intel/`, `cross-platform/`, `promotions/`. Hunting queries are in `hunting/` |

Endpoint agent internals are not in a public repo. When a claim depends on them, it is an open question for the Defend team rather than something to verify yourself.

## Read these first

- `solutions/security/detect-and-alert/alert-suppression.md` — the model for a feature page. Full frontmatter, a lead paragraph that states the problem before the feature, and a `::::{admonition} Requirements` block covering subscription and ML prerequisites.
- `solutions/security/detect-and-alert/choose-the-right-rule-type.md` — the model for a decision page. Opens by naming the reader's question, then answers it with a comparison table whose rows are explicitly ordered as a decision flow.
- `solutions/security/investigate.md` — the model for a section landing page, including a `navigation_title` that differs from the H1.

## Local conventions

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

Use the substitutions rather than typing product names: `{{elastic-sec}}` for Elastic Security, `{{elastic-defend}}` for Elastic Defend, `{{elastic-endpoint}}` for Elastic Endpoint, `{{ml-cap}}` for Machine learning, `{{serverless-short}}` for Serverless.

Headings carry explicit anchor IDs in brackets, on the H1 and on section headings — `# Suppress detection alerts [security-alert-suppression]`. Existing anchors are load-bearing because they preserve legacy deep links, so never change or remove one on an existing page. New headings get a new stable slug.

Feature prerequisites go in a `::::{admonition} Requirements` block near the top, not scattered through the page.

## Navigation

`solutions/toc.yml` — a single file of roughly 870 lines that holds the whole Security tree inline, starting at the `- file: security.md` entry. There is **no** `solutions/security/toc.yml`, and adding one will not work; `docset.yml` maps the `solutions` toc as one unit.

`reference/security/` is the exception: it has its own `reference/security/toc.yml`.

Add the page to its parent's `children:` list in the position it should appear, since order in the file is the order in the sidebar. Then link it from the subdirectory's landing page. That landing page is normally a **sibling** of the directory rather than an `index.md` inside it — `detect-and-alert.md` sits next to `detect-and-alert/`. The pattern is not universal, though: `ai/attack-discovery/` uses an inner `index.md`. Check the actual directory instead of assuming either shape.

## Known traps

- **Defend, Endpoint, and detection rules are three different things.** {{elastic-defend}} is the integration users configure, {{elastic-endpoint}} is the agent component, and detection rules are content shipped from `detection-rules`. Requests conflate them constantly. Establish which one the change touches before choosing a directory.
- **Detection rule content is not documented in docs-content.** A request to "document a new rule" usually belongs in the `detection-rules` repo. Confirm before drafting a page that should not exist.
- **Configure versus manage Defend.** Two sibling directories with a genuine split. Setting up a policy is *configure*; operating it afterward is *manage*. Guessing produces a page that is hard to find.
- **Serverless Security has product tiers, and there is no frontmatter field for them.** Tier requirements such as Security Complete are written in prose, typically in the Requirements admonition. Do not invent a `product_tier` key.
- **Reference tables belong in `reference/security/`.** Long field, setting, and command tables have a home. Adding one to a narrative page in `solutions/security/` is a common review comment.
- **The Kibana plugin moved.** Paths under `x-pack/plugins/security_solution/` are stale; the current tree is `x-pack/solutions/security/plugins/security_solution/`. Verifying against a stale path silently finds nothing and looks like a missing feature.
