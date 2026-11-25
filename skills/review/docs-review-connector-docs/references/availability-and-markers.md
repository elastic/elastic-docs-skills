# Availability and API-only markers

Read this before writing any comment about where a connector or an action is available.

## Three independent signals

| Signal | Scope | Meaning |
|---|---|---|
| `supportedFeatureIds` contains `agentBuilder` | Connector type | Agent Builder lists the connector. |
| `supportedFeatureIds` contains `workflows` | Connector type | Workflows lists the connector and offers every action in its spec as a step. |
| An action has `isTool: true` | One action | Agent Builder can offer that action to agents. The default is false. |

Agent Builder turns only actions with `isTool === true` into tools (`filterActionsBySelection` in `selected_actions.ts`). An action with `isTool: false` defaults to the `destroy` scope (`resolveActionScope`), so these are usually the write and destructive actions.

`isTool: false` doesn't make an action "workflow-only". It keeps the action away from agents. Workflows gets it only once the connector declares `workflows`. Until then, the action runs only through the Run a connector (`_execute`) API.

Don't treat a PR title such as `[Workflows][Connectors]` as proof of Workflows availability. Read the spec.

## Two-step release for new connector types

New connector types ship in two steps, so a Serverless rollback can't leave workflows that reference an unregistered type:

1. The first PR ships `supportedFeatureIds: ['agentBuilder']`.
2. A follow-up PR adds `workflows` once the type is in every production Serverless version.

Classify a page's Workflows claim:

- **Confirmed:** the spec includes `workflows`.
- **Planned alignment:** the page scopes Workflows to a future version and a known follow-up PR adds it. Don't report this as a defect.
- **Mismatch:** the page presents Workflows as available now and the spec doesn't include it. Report it.
- **Unclear:** you can't find the follow-up. Ask the developer.

`serverless` is unversioned. A bare `serverless: preview` promises availability as soon as the page publishes, so check it separately from the Stack version.

## The marker policy

On an Agent Builder-only connector, recommend `_(API only)_` on every `isTool: false` action, explained once near the top. "Not yet available" doesn't tell readers what they can do with these actions today. They already work through the API.

Standard note, when the page has no explanation yet:

```markdown
This connector is currently available in **Agent Builder** only. Workflow support is planned for a future release. Actions marked _(API only)_ aren't available to agents yet. You can run them with the [Run a connector](https://www.elastic.co/docs/api/doc/kibana/operation/operation-post-actions-connector-id-execute) API.
```

If the page already explains the marker in its own words, keep the author's wording and only swap the marker.

Then post one suggestion per marked action line, on the definition term:

```markdown
`deleteIndicator` _(API only)_
```

Also swap the marker in any other sentence that uses it. A summary table marker doesn't replace the marker on the action's own entry.

Other rules:

- Keep "Workflow support is planned for a future release." It's the only future-looking sentence the pages allow. Don't add other promises.
- Don't flag a description, intro, or connector-list line because it lists an API-only action next to the others. These actions will be fully supported later.
- If the connector declares `workflows`, there's nothing to mark. The test then fails on any leftover marker.

## The contract test

`src/platform/packages/shared/kbn-connector-specs/src/connector_spec_quality_contract.test.ts` checks every connector page unless the spec sets `metadata.docsUrl`. When it applies:

- The availability statement must match: `**Agent Builder** only` for an Agent Builder-only connector.
- Every non-tool action must have the exact text `_(not yet available)_` on its own line while the connector lacks `workflows`.
- Only non-tool actions may end with that marker.
- Workflow-use phrases and internal vocabulary are rejected.
- Links in the toc and snippet must point to existing pages.

So `_(API only)_` fails CI on pages without `docsUrl`. Recommend it anyway, and add this heads-up line after the suggestion:

```markdown
Heads-up: `connector_spec_quality_contract.test.ts` checks these lines for the old `_(not yet available)_` text, so it needs a matching change there.
```

Skip the heads-up when the spec sets `docsUrl`, because the test doesn't check that page. Before claiming either way, grep the spec at the PR head for `docsUrl` and check whether the PR changes the test.

The Kibana `create-connector` and `review-connector` skills still tell authors to use `_(not yet available)_`. Expect new PRs to arrive with it until those skills change.
