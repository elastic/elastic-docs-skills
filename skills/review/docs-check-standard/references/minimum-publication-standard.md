# Minimum publication standard (checklist)

This file holds the requirements that the `docs-check-standard` skill applies. It is kept outside the skill so the standard can change without editing the skill, and so other things (the self-certification checklist, the epic definition of done, the partner guidance) can point at one list.

- **Source of truth:** the "Minimum publication standard" section of the Documentation Engagement Model. This checklist expands its requirements into items a reviewer can mark. If the two disagree, the Engagement Model wins and this file should be updated.
- **Owner:** TBD. Someone needs to own changes to this list.
- **Canonical home:** TBD. The intended home is a page in the contribute docs in `docs-content`. Until that page exists, this file is the bundled copy.
- **Not in this file:** how to review (diff scoping, FAIL versus verify rules, report format). Those stay in the skill. The ownership requirement (named docs DRI, named owner for updates) is not marked per file: the skill prints it as a fixed Verify line.

## How each requirement is marked

- PASS: the requirement is clearly met
- FAIL: the requirement is not met in the changed content and must be resolved before publishing
- NEEDS REVIEW: it cannot be determined from the files alone, so the author must verify
- N/A: the requirement does not apply to this kind of page or change. Skip it silently.

## Requirements

Each requirement has a stable ID. Findings cite the ID. Do not rename or reuse an ID: other skills (`docs-review-pr`) and evals refer to them.

**Audience and purpose**
- `PS-audience` Clear intended audience stated or clearly implied
- `PS-goal` Customer goal explicitly stated or clearly implied
- `PS-assumptions` No unexplained assumptions about audience knowledge

**Availability and prerequisites**
- `PS-deployment` Deployment types clearly stated
- `PS-tier` Subscription tier or license requirements documented
- `PS-permissions` Required permissions documented
- `PS-prereqs` Prerequisites and dependencies documented
- `PS-config` Configuration steps documented

**Core content**
- `PS-task` Primary customer task documented end to end
- `PS-verifiable` Steps are verifiable
- `PS-examples` Examples included where applicable
- `PS-code` API calls, commands, and code samples present where applicable

**Limitations and risks**
- `PS-limitations` Known limitations documented
- `PS-risks` Risks and consequences documented
- `PS-irreversible` Data loss, security, compliance, or irreversible actions explicitly called out

**Terminology and accessibility**
- `PS-terminology` Terminology consistent with existing Elastic documentation (use MCP results to verify)
- `PS-ui-labels` UI element names and labels match standard Elastic conventions
- `PS-headings` Headings are hierarchical
- `PS-alt-text` Images have alt text where applicable
- `PS-table-headers` Tables have headers where applicable

**Lifecycle**
- `PS-lifecycle` Lifecycle status documented
