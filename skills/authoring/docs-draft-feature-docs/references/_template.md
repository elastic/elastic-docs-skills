# <Area name>

*One or two sentences: what this area covers, and where its boundary sits against neighboring areas. Spend more of them on the boundary than on the description, because the boundary is what keeps a page out of the wrong docset.*

*If the area is not in docs-content, say so here, in bold, before anything else. A published URL under `elastic.co/docs/` is not evidence of which repo owns the page.*

> *Required. Replace with: the repos and date you verified this file against, plus any restructure, migration, or rename already known to be coming, with its tracking issue. A confident fact that has since changed is the main way an area file does damage.*

## What belongs here, and what does not

*The boundary, as judgment rather than inventory. Which kinds of content this area owns, which kinds get misfiled into it, and where those actually belong. This is usually the most-used section.*
    
*Name a directory only when the decision turns on it — a genuine split such as configure versus manage, or reference tables that live outside the narrative tree. Note any `_snippets/` directory to check before writing shared prose.*

| The content is | Home |
|---|---|
| | |

## Source of truth

*Which repo and which paths settle a question about behavior, and what each one answers. Be specific enough to grep: a plugin directory is useful, a repo name alone is not. Name the separate source for each kind of fact when they differ, because UI strings, API parameters, and defaults often live apart.*

*Fill this in carefully. Neither the MCP nor the published docs can answer these questions, so this section is the main reason the file exists.*

| Question | Verify at |
|---|---|
| UI labels and strings | |
| Settings and defaults | |
| API parameters | |

## Conventions

*Only what differs from the baseline or is not derivable from a sibling page: terminology this area uses and the words it avoids, substitutions, required frontmatter values, standard section ordering, how product names and tiers are written here.*

*Nothing in this section may contradict the style guide, content types, or cumulative-docs rules. It narrows choices the baseline leaves open; it does not reopen ones the baseline has settled.*

*Name one or two model pages and say what each is a good example of — a feature page, a decision page, a landing page. Two is enough; the MCP finds the rest.*

## Navigation

*Which `toc.yml` to edit and where in it, since navigation is not published and so the MCP cannot see it. Some sections keep a whole tree inline in one file while others nest sub-tocs, so name the actual file and the actual parent entry.*

*Record the landing-page shape rather than assuming it: a sibling file next to the directory, an `index.md` inside it, or a name that matches neither. Note any `hidden:` entries, which look like omissions but are deliberate. Say when a change needs no navigation edit at all.*

## Known traps

*The mistakes people actually make here, and what to do instead. Usually the last section written, because it comes from review feedback rather than from reading the repo.*

*Good traps: a label that changed and whose old name still appears in the docs; two similarly named features that get conflated; a setting whose behavior differs between deployment types; a page that looks like the right home but is not; a source path that moved.*

---

## Writing one of these

**If `search_docs` can answer it, do not write it here.** The MCP knows every published page, so a page inventory in this file is maintenance work that buys nothing and goes stale between releases. Record what the MCP cannot know: boundaries, product source paths, local conventions, navigation files, and traps.

Two more rules:

- **No line counts, file counts, or page lists.** They are stale within a release and never change a decision.
- **Every line has to change a decision.** Length follows from how much the area actually has that the baseline and the MCP do not — `agent-builder.md` needs about 60 lines and `workflows.md` needs closer to 100. Neither is a target. When a file grows past 100, check whether it is really two areas before adding to it.
