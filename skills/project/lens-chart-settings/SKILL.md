---
name: docs-lens-chart-settings
version: 1.0.1
description: Verify Kibana Lens chart UI settings against the source code. Use when documenting chart types, reviewing chart settings accuracy, or checking UI labels and rendering order for Lens visualizations (bar, line, area, pie, treemap, mosaic, waffle, tag cloud, heat map, gauge, metric, region map, table).
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
  - https://github.com/elastic/kibana/tree/main/x-pack/platform/plugins/shared/lens/public/visualizations
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

# Verifying Kibana Lens Chart Settings from Source Code

When documenting Lens chart settings, always verify labels, options, and rendering order against the Kibana source code. Do NOT guess UI labels.

## Key Principles

1. **UI labels come from i18n `defaultMessage` strings** — always extract the exact label.
2. **Rendering order in JSX = rendering order in the UI** — document settings in the same order they appear in the component tree.
3. **Conditional rendering is everywhere** — many settings only appear under specific conditions (chart type, selected options, number of dimensions). Trace the conditions.
4. **Shared components are parameterized per chart** — the same `LegendSettings` component behaves differently for treemaps vs waffle vs pie based on props.

## Source Code Layout

### Partition charts (pie, donut, treemap, mosaic, waffle)

All partition-type charts share code under:

```
x-pack/platform/plugins/shared/lens/public/visualizations/partition/
├── partition_charts_meta.ts          # Per-chart config (toolbar options, legend config)
├── toolbar/
│   ├── style_settings.tsx            # Orchestrates Style panel sections
│   ├── titles_and_text_setttings.tsx # Slice labels + Slice values options
│   ├── appearance_settings.tsx       # Donut hole (pie/donut only)
│   └── legend_settings.tsx           # Partition-specific legend wrapper
```

Shared legend component:

```
x-pack/platform/plugins/shared/lens/public/shared_components/legend/
├── legend_settings.tsx               # Main legend settings (Visibility, Size, Truncation, Nested, Stats)
├── location/legend_location_settings.tsx  # Position (only when `location` prop is defined)
└── size/legend_size_settings.tsx     # Width/Size dropdown
```

### Other chart types

Each chart type has its own directory under `visualizations/`:
- `visualizations/xy/` for bar, line, area
- `visualizations/heatmap/`
- `visualizations/gauge/`
- `visualizations/metric/`
- `visualizations/tagcloud/`

## Verification Workflow

### Step 1: Find the chart metadata

For partition charts, start with `partition_charts_meta.ts`. This file defines per-chart:
- `toolbar.categoryOptions` — Slice labels options (or empty array if none)
- `toolbar.numberOptions` — Slice values options (or empty array if none)
- `toolbar.emptySizeRatioOptions` — Donut hole options (pie/donut only)
- `toolbar.isDisabled` — Whether the Style panel is disabled entirely (waffle)
- `legend.defaultLegendStats` — Enables Statistics/Show value in legend (waffle only)
- `legend.hideNestedLegendSwitch` — Hides the Nested toggle (waffle)
- `legend.getShowLegendDefault` — Default legend visibility behavior for Auto mode
- `maxBuckets` — Maximum Group by dimensions

### Step 2: Trace the Style settings

Read `toolbar/style_settings.tsx` to understand the Style panel structure:

- If `emptySizeRatioOptions` exists → renders **Appearance** accordion + **Titles and text** accordion
- If not → renders only `PartitionTitlesAndTextSettings` directly (no sub-headers)

Then read `toolbar/titles_and_text_setttings.tsx`:
- `categoryOptions` renders as the first button group (label: check i18n key `xpack.lens.pieChart.labelSliceLabels`)
- `numberOptions` renders as the second button group (label: check i18n key `xpack.lens.pieChart.sliceValues`)
- If `numberDisplay === 'percent'`, a **Decimal places** input appears

If `categoryOptions` is empty, the first button group is hidden. If `numberOptions` is empty, the second button group is hidden. If `isDisabled` is true, the entire section is disabled/hidden.

### Step 3: Trace the Legend settings

Read `toolbar/legend_settings.tsx` (partition wrapper) to see what props are passed to the shared `LegendSettings` component. Key props to check:

| Prop | What it controls | How to verify |
|------|-----------------|---------------|
| `legendOptions` | Visibility options (Auto/Show/Hide) | Always present for all partition charts |
| `position` | Only renders if `location` is also passed | Partition charts do NOT pass `location` → Position hidden |
| `renderNestedLegendSwitch` | Nested toggle | `!hideNestedLegendSwitch && groups > 1` |
| `allowedLegendStats` | Statistics/Show value | Only if `defaultLegendStats` defined in chart meta |
| `legendSize` / `onLegendSizeChange` | Width dropdown | Renders if `isVerticalLegend` is true |
| `shouldTruncate` / `onTruncateLegendChange` | Label truncation toggle | Always present when legend not hidden |
| `showAutoLegendSizeOption` | Auto in size dropdown | Only for pre-8.3 visualizations |

### Step 4: Determine rendering order

Read the shared `legend_settings.tsx` JSX top to bottom. For partition charts (no `location` prop), the actual rendering order is:

1. **Visibility** (always)
2. **Width** (when legend not hidden, via LegendSizeSettings)
3. **Label truncation** + **Line limit** (when legend not hidden)
4. **Nested** (when legend not hidden AND multiple groups AND not hideNestedLegendSwitch)

Settings that do NOT render for partition charts:
- **Position** — requires `location` prop (only XY charts pass this)
- **Statistics** — requires `allowedLegendStats.length > 1`
- **Show value** — requires exactly 1 allowed legend stat of type Value/CurrentAndLastValue

### Step 5: Verify option labels

For each button group or dropdown, check the `label` or `inputDisplay` in the options array. Common pitfalls:

| What you might assume | Actual UI label | Source |
|-----------------------|----------------|--------|
| "Labels" | "Slice labels" | `xpack.lens.pieChart.labelSliceLabels` |
| "Values" | "Slice values" | `xpack.lens.pieChart.sliceValues` |
| "Legend size" | "Width" | `xpack.lens.shared.legendSizeSetting.label` |
| "Truncate" | "Label truncation" | `xpack.lens.shared.labelTruncation` |
| "Max lines" | "Line limit" | `xpack.lens.shared.maxLinesLabel` |
| "Show" (legend) | "Show" | `xpack.lens.pieChart.legendVisibility.show` |

## Quick Reference: Per-Chart Differences

| Feature | Pie/Donut | Treemap | Mosaic | Waffle |
|---------|-----------|---------|--------|--------|
| Slice labels | Hide/Inside/Auto | Hide/Show | (none) | (none) |
| Slice values | Hide/Integer/Percentage | Hide/Integer/Percentage | Hide/Integer/Percentage | (none) |
| Donut hole | Yes | No | No | No |
| Style panel disabled | No | No | No | Yes |
| Legend Position | No | No | No | No |
| Legend Width | Yes | Yes | Yes | Yes |
| Nested legend | Yes (>1 group) | Yes (>1 group) | Yes (>1 group) | No |
| Show value | No | No | No | Yes |
| Statistics | No | No | No | No |
| Default legend visibility | Auto shows when >1 bucket | Auto hides | Auto hides | Auto shows always |
| Max Group by dimensions | 3 | 2 | 2 | 1 |
| Color mapping | First Group by only | First Group by only | Vertical axis | Group by |

## Common Mistakes to Avoid

1. **Assuming Position exists for partition charts** — it doesn't. Only XY-type charts have Position.
2. **Using "Legend size" instead of "Width"** — the actual label is "Width".
3. **Including Auto in Width options** — Auto only shows for pre-8.3 visualizations.
4. **Documenting Statistics for non-waffle charts** — only waffle has `defaultLegendStats`.
5. **Assuming "Titles and text" sub-header exists for all charts** — it only appears when `emptySizeRatioOptions` is defined (pie/donut).
6. **Getting the Nested legend condition wrong** — it requires both `hideNestedLegendSwitch !== true` AND multiple Group by dimensions.
7. **Assuming color mapping works on all Group by levels** — only available on the first dimension.
