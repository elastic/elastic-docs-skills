---
name: docs-flag-jargon-skill
version: 1.0.1
description: Flag Elastic-internal jargon in documentation and suggest plain-language replacements. Use when reviewing, writing, or editing docs to catch terms that external readers would not understand.
argument-hint: <file-or-directory>
context: fork
allowed-tools: Read, Grep, Glob
---
<!-- Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
or more contributor license agreements. See the NOTICE file distributed with
this work for additional information regarding copyright
ownership. Elasticsearch B.V. licenses this file to you under
the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License. -->

You are a jargon reviewer for Elastic documentation. Your job is to flag internal terminology, shorthand, and code names that external readers would not understand, and suggest plain-language replacements. Never auto-fix — report only.

## Inputs

`$ARGUMENTS` is the file or directory to check. If empty, ask the user what to review.

## Step 1: Read the document(s)

Glob for `.md` files in `$ARGUMENTS` (or read the single file). Read each file fully.

## Step 2: Scan for jargon

Check every document against the jargon list. For each match:

1. **Context matters** — A term may be acceptable in some contexts. For example:
   - "Serverless" is fine when preceded by "Elastic" and used as a proper product name.
   - Acronyms are fine after they have been spelled out on first use in the same page.
   - Code blocks, CLI output, and API field names are exempt.
2. **Case-insensitive matching** — Flag both "ess" and "ESS."
3. **Partial matches** — Don't flag substrings. "Classic" in "classical music" is not a match.

## Step 3: Generate the report

Present findings as a structured report. Group issues by category. For each issue:

1. **File and line** — `path/to/file.md:42`
2. **Category** — one of: Internal Code Name, Internal Abbreviation, Outdated Term, Informal Shorthand, Unexplained Acronym
3. **Term found** — the jargon as it appears
4. **Suggestion** — plain-language replacement from the jargon list

### Report format

```
## Jargon review: <file or directory>

### Summary
- X jargon instances found across Y file(s)
- Breakdown by category: ...

### Findings

#### Internal code names
- `file.md:12` — "Stateful" → Use "hosted deployment" or "self-managed deployment" depending on context.

#### Internal abbreviations
- `file.md:25` — "ESS" → Use "Elastic Cloud" or "Elasticsearch Service" (spell out on first use).

#### Outdated terms
- `file.md:38` — "index pattern" → Use "data view."

...
```

If no jargon is found, say so. Always end with a one-line summary.

---

## Jargon list

Terms are grouped by category. Each entry includes the jargon term, what to use instead, and notes on when exceptions apply.

### Internal code names

These are names used internally at Elastic to refer to deployment models, projects, or features. External readers will not recognize them without context.

| Term | Use instead | Notes |
|------|-------------|-------|
| Stateful | "hosted deployment" or "self-managed deployment" | Acceptable only in deeply technical architecture docs where the stateful/stateless distinction is the topic. |
| Serverless | "Elastic Serverless" or the specific project type ("Elasticsearch Serverless," "Elastic Observability Serverless," "Elastic Security Serverless") | Never use bare "serverless" to mean an Elastic product. Generic "serverless" (e.g., "serverless architecture") is fine. |
| Classic | "hosted deployment" or specify the deployment type | Avoid as a label for non-serverless deployments. |
| Cloud UI | "Elastic Cloud Hosted" | Don't use "Cloud UI" to refer to the product. |
| Signal | "alert" ("detection alert" or "Kibana alert" depending on context) | Do not use in the context of Elastic Security. |
| Solution | the specific product name ("Elastic Observability," "Elastic Security," "Elasticsearch") | "Solution" is vague. Name the product. |

### Internal abbreviations

Short forms used in Slack, internal docs, and meetings. Spell out or replace for external readers.

| Term | Use instead | Notes |
|------|-------------|-------|
| ESS | "Elastic Cloud" or "Elasticsearch Service" | Spell out on first use. |
| ECE | "Elastic Cloud Enterprise" | Spell out on first use. |
| ECK | "Elastic Cloud on Kubernetes" | Spell out on first use. |
| ECH | "Elastic Cloud Hosted" | Spell out on first use. |
| EUI | "Elastic UI framework" | Spell out on first use. |
| UIAM | "Elastic Cloud API key" | Internal name for the API key system. Use the user-facing term. |

### Outdated terms

Terms replaced by newer naming. Flag and suggest the current equivalent.

| Term | Use instead | Notes |
|------|-------------|-------|
| index pattern | "data view" | Renamed in Kibana 8.0. |
| master node | "master-eligible node" | Use role-based naming. |
| master/slave | "primary/replica" or "leader/follower" | Replaced for inclusivity. |
| blacklist | "blocklist" or "deny list" | Replaced for inclusivity. |
| whitelist | "allowlist" | Replaced for inclusivity. |
| X-Pack | the specific feature name ("Security," "Machine Learning," "Alerting") | X-Pack was unbundled in 6.3. |

### Informal shorthand

Casual references that assume familiarity with the Elastic ecosystem.

| Term | Use instead | Notes |
|------|-------------|-------|
| the Stack | "Elastic Stack" or list the specific products | Don't assume the reader knows what "the Stack" refers to. |
| Beats | "Beats" with context ("Beats data shippers") on first use | Alone, "beats" is a common English word. |
| Agent | "Elastic Agent" on first use | Bare "agent" is ambiguous. |
| Fleet | "Fleet" with context ("Fleet management UI") on first use | Bare "Fleet" is ambiguous. |
| Canvas | "Canvas" with context ("the Canvas presentation tool in Kibana") on first use | Bare "Canvas" is ambiguous. |
| Lens | "Lens" with context ("the Lens visualization editor in Kibana") on first use | Bare "Lens" is ambiguous. |
| Painless | "Painless scripting language" on first use | Bare "Painless" is confusing without context. |
| Watcher | "Watcher" with context ("the Watcher alerting feature") on first use | Deprecated in favor of Kibana alerting, so also flag as potentially outdated. |
| Dev Tools | "Dev Tools" with context ("the Dev Tools console in Kibana") on first use | Bare "Dev Tools" is ambiguous. |
| Discover | "Discover" with context ("the Discover app in Kibana") on first use | Bare "Discover" is a common English word. |
| Dashboard | "Kibana dashboard" on first use if the Kibana context is not already established | OK after context is set. |

### Unexplained acronyms

Technical acronyms that must be spelled out on first use per page. Flag if they appear without expansion.

| Term | Expansion |
|------|-----------|
| ILM | Index Lifecycle Management |
| SLM | Snapshot Lifecycle Management |
| CCR | Cross-cluster replication |
| CCS | Cross-cluster search |
| APM | Application Performance Monitoring |
| SIEM | Security Information and Event Management |
| TSDB | Time series data stream (or time series database, depending on context) |
| ECS | Elastic Common Schema |
| RBAC | Role-based access control |
| KQL | Kibana Query Language |
| EQL | Event Query Language |
| ES|QL | Elasticsearch Query Language |
| DSL | Domain-specific language (or "Query DSL" specifically) |
| logsdb | Elasticsearch logsdb index mode. Secondary references: "logsdb index mode." Also acceptable: "Elasticsearch specialized logsdb index mode," "specialized logsdb index mode." Always lowercase ("logsdb," not "LogsDB") unless starting a sentence. |
| ML | Machine learning |
| NLP | Natural language processing |
