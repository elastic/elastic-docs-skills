# Kibana 9.5.0 Release Notes

## Features (release_note:feature)

### Search

- Adds semantic search support in Search Playground #213100(opens in a new tab or window)

## Enhancements (release_note:enhancement)

### Connectors

- Adds MCP connector for external tool integration #213400(opens in a new tab or window)

## Breaking Changes

### Platform

- Removes deprecated `xpack.security.authProviders` setting. Use `xpack.security.authc.providers` instead. #213700(opens in a new tab or window)

## Deprecations

### Fleet

- Deprecates `fleet.agents.elasticsearch.host` setting in favor of `fleet.agents.elasticsearch.hosts` #214000(opens in a new tab or window)

## Fixes (release_note:fix)

### Dashboards

- Fixes panel duplication when cloning a dashboard with linked saved searches #214300(opens in a new tab or window)
