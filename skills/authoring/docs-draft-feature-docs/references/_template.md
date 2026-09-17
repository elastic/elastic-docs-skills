# <Area name>

One or two sentences: what this area covers, and where its boundary sits against neighboring areas. The boundary matters more than the description — it is what stops a page from being drafted into the wrong docset.

*If the area is not in docs-content, say so here, in bold, before anything else. A published URL under `elastic.co/docs/` is not evidence of which repo owns the page.*

> *Required. Replace with: the repo and date you verified this file against. Add any restructure, migration, or rename already known to be coming, with the tracking issue and what it will make stale. A confident path that has since moved is the main way an area file does damage.*

Fill all six headings below. Delete the guidance in italics as you go. Verify every path and label before it goes in, because this file becomes a source of truth for everyone who drafts here.

## Where content lives

*The paths this area owns, and what belongs in each. Name the repo when it is not docs-content. Include the `_snippets/` directories to check before writing shared prose, and note any content that lives outside the obvious docset — for example, reference material under `reference/` while the narrative sits under `solutions/`.*

*Add a "Not this area" list for the paths people most often misfile into, with a one-line reason each. This is usually the most-used part of the file.*

| Path | What belongs here |
|---|---|
| | |

## Source of truth

*Which repo and which paths settle a question about behavior, and what each one answers. Be specific enough to grep: a plugin directory is useful, a repo name alone is not. Name the separate source for each kind of fact when they differ — UI strings, API parameters, and defaults often live apart.*

| Question | Verify at |
|---|---|
| UI labels and strings | |
| Settings and defaults | |
| API parameters | |

## Read these first

*Two or three existing pages that best represent the area. New drafts should look like these. Say what each one is a good example of, so the reference is usable rather than decorative.*

## Local conventions

*Only what differs from the baseline or is not derivable from sibling pages: terminology this area uses and the words it avoids, required frontmatter values, standard section ordering, recurring admonitions or snippets, how product names and tiers are written here.*

*Nothing in this section may contradict the style guide, content types, or cumulative-docs rules. It narrows choices the baseline leaves open; it does not reopen ones the baseline has settled.*

## Navigation

*Which `toc.yml` to edit, and where in it. Navigation is per-docset and orchestrated by `docset.yml` — some sections keep a whole tree inline in one file while others nest sub-tocs, so name the actual file and the actual parent entry. Note any hub or index page that also needs a link, and say when a change needs no navigation edit at all.*

*Record the landing-page shape rather than assuming it: a sibling file next to the directory, an `index.md` inside it, or a name that matches neither. Note any `hidden:` entries, which look like omissions but are deliberate.*

## Known traps

*The mistakes people actually make here, and what to do instead. This is the highest-value section and usually the last one written, because it comes from review feedback rather than from reading the repo.*

*Good traps: a label that changed and whose old name still appears in the docs; two similarly named features that get conflated; a setting whose behavior differs between deployment types; a page that looks like the right home but is not.*
