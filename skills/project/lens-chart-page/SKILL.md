---
name: lens-chart-page
version: 1.0.0
description: Create or update a Lens chart documentation page following Elastic docs conventions. Use when writing a new chart type page (pie, bar, metric, gauge, heat map, etc.) or updating an existing one in explore-analyze/visualize/charts/. Relies on lens-chart-settings for verifying UI labels against source code.
allowed-tools: Read, Grep, Glob, Edit, WebFetch
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

# Creating Lens Chart Documentation Pages

Use these instructions when creating or updating a documentation page for a Kibana Lens chart type in `explore-analyze/visualize/charts/`.

## Before writing: verify settings against source code

Use the **lens-chart-settings** skill to verify all UI labels, option values, and rendering order against the Kibana source code before documenting them. Never guess UI labels.

## Research resources

### Kibana source code paths

| Chart type | Source path |
|------------|-------------|
| Partition (pie, donut, treemap, mosaic, waffle) | `x-pack/platform/plugins/shared/lens/public/visualizations/partition/` |
| XY (bar, line, area) | `x-pack/platform/plugins/shared/lens/public/visualizations/xy/` |
| Metric | `x-pack/platform/plugins/shared/lens/public/visualizations/metric/` |
| Datatable | `x-pack/platform/plugins/shared/lens/public/visualizations/datatable/` |

Many visualizations use **shared components** (in `shared_components/`) that accept different props per chart. Always check the visualization-specific wrapper to see which props are passed, rather than assuming all shared component options are available.

### EUI data visualization guidelines

- [Part-to-whole comparisons](https://eui.elastic.co/docs/dataviz/types/part-to-whole-comparisons/) (pie, donut, treemap)
- [Dashboard good practices](https://eui.elastic.co/docs/dataviz/dashboard-good-practices/)
- [Categorical color palettes](https://eui.elastic.co/docs/dataviz/guides/color-guidelines/)

### Existing content to check

- **Main Lens page**: `explore-analyze/visualize/lens.md` — check for content to reference or deduplicate.
- **Other chart pages**: `explore-analyze/visualize/charts/*.md` — follow established patterns.
- **Shared snippets**: `explore-analyze/_snippets/lens-*.md` — reuse instead of duplicating.

Key snippets:

| Snippet | Purpose |
|---------|---------|
| `lens-prerequisites.md` | Prerequisites paragraph (data views, ES\|QL mode) |
| `lens-rank-by-options.md` | Top values rank-by options |
| `lens-value-advanced-settings.md` | Advanced settings for value/metric dimensions |
| `lens-breakdown-advanced-settings.md` | Breakdown advanced settings |
| `lens-histogram-settings.md` | Date histogram settings |
| `line-chart-legend-settings.md` | Legend settings including Statistics (line/area) |
| `line-chart-style-settings.md` | Style settings (line/area) |

When creating a new chart page, update `lens.md` to link to it and remove any duplicated content.

## File location and frontmatter

Place the file at `explore-analyze/visualize/charts/<chart-type>.md` with this frontmatter:

```yaml
---
navigation_title: <Chart type> charts
applies_to:
  stack: ga
  serverless: ga
description: Instructions and best practices for building <chart type> charts with Kibana Lens in Elastic.
---
```

## Chart-specific dimensions

| Chart type | Primary dimensions | Additional dimensions |
|------------|-------------------|----------------------|
| Pie / Donut | **Slice by**, **Metric** | (none) |
| Bar / Line / Area | **Horizontal axis**, **Vertical axis** | **Breakdown** |
| Metric | **Primary metric** | **Secondary metric**, **Maximum value** |
| Gauge | **Metric** | **Minimum value**, **Maximum value**, **Goal** |
| Table | **Metrics**, **Rows** | **Split metrics by** |

## Page structure

Follow this exact section order. Every chart page uses it consistently.

### 1. Title and introduction

```
# Build <chart type> charts with {{kib}}
```

- One paragraph (2-3 sentences): what the chart does and when it's useful. Focus on purpose.
- Weave in specific actionable constraints (e.g., "works best with a maximum of 6 slices"). Skip generic advice.
- Do **not** create a separate "When to use" section.
- A line: `You can create <chart type> charts in {{kib}} using [**Lens**](../lens.md).`
- A hero image of a representative example.

### 2. "Build a <chart type> chart" section

Include the prerequisites snippet before the stepper:

```
:::{include} ../../_snippets/lens-prerequisites.md
:::
```

Then use the `stepper` directive:

```
::::::{stepper}

:::::{step} Access Lens
**Lens** is {{kib}}'s main visualization editor. You can access it:
- From a dashboard: On the **Dashboards** page, open or create the dashboard where you want to add a <chart type> chart, then add a new visualization.
- From the **Visualize library** page by creating a new visualization.
:::::

:::::{step} Set the visualization to <Chart type>
New visualizations often start as **Bar** charts.

Using the **Visualization type** dropdown, select **<Chart type>**.
:::::

:::::{step} Define the data to show
[Chart-specific data configuration steps]
:::::

:::::{step} Customize the chart to follow best practices
[Best practices as a definition list]
:::::

:::::{step} Save the chart
- If you accessed Lens from a dashboard, select **Save and return** to save the visualization and add it to that dashboard, or select **Save to library** to add the visualization to the Visualize library and reuse it later.
- If you accessed Lens from the Visualize library, select **Save**. A menu opens and offers you to add the visualization to a dashboard and to the Visualize library.
:::::

::::::
```

Key conventions:
- **Access Lens** and **Save the chart** steps are identical across all chart pages. Copy them verbatim.
- **Define the data to show** lists numbered steps for chart-specific dimensions, then "Optionally:" for additional dimensions. Link dimension names to their settings sections (e.g., `[**Slice by**](#slice-by-settings)`).
- **Customize the chart** uses **definition list** format. List 4-6 actionable best practices. End with a line pointing to the full settings reference.

### 3. Advanced scenarios (optional)

Only include when teaching a non-obvious technique users wouldn't discover on their own:
- Using **formulas** (e.g., computing error rates as a percentage)
- Configuring **multiple metrics** for completion progress (waffle)
- Setting up **dynamic bounds or goals** from data (gauge)
- Defining **custom color ranges** (heat map)
- Configuring **color bands** with thresholds (gauge)

Do NOT create scenarios that are just "use the chart with different fields". For simpler chart types, the Examples section is sufficient.

When including scenarios:
- Each scenario gets its own `##` or `###` heading with an anchor ID.
- Use concrete examples based on **Kibana Sample Data** when possible.

#### Sample data considerations

- The `response` field in web logs is a **text** field — KQL filters must use pattern matching (`response: 2*`), not numeric comparisons.
- In sample ecommerce data, `taxful_total_price` and `taxless_total_price` are identical.
- Multiple comparable numeric fields are rare. When sample data doesn't support a scenario, use a conceptual example with realistic field names and add a `:::note` explaining users need to adapt to their data.

### 4. "<Chart type> settings" section

Document **every** configuration option in the Lens editor, organized by dimension/panel.

Structure each dimension as:

```
### <Dimension> settings [<dimension>-settings]
```

Within each dimension, use **two top-level definition list entries**: `**Data**` and `**Appearance**`.

**Data**:
- List all available functions/aggregation types.
- For each function, document the **Field** selector first, then function-specific sub-options as nested bullets.
- **Field selector conventions**:
  - **Top values**: Supports up to 4 fields. Multiple fields create multi-term grouping. Fields can be reordered by dragging.
  - **Date histogram**: Single date field only.
  - **Intervals**: Single numeric field only.
  - **Filters**: No field selector (KQL queries reference fields directly).
- Reuse shared snippets wherever applicable.

**Appearance**:
- List visual options: Name, Value format, Color, Series color, Color mapping, etc.

After dimension-specific settings, add a `### General layout` section for global settings ({icon}\`brush\` **Style** and legend). Split into `#### Style settings` and `#### Legend settings` as needed.

**Legend settings** vary by chart type:

| Setting | XY charts | Partition charts | Notes |
|---------|-----------|-----------------|-------|
| Visibility | Yes | Yes | Auto / Show / Hide |
| Position | Yes | No | Partition charts don't pass `location` |
| Statistics | Yes | No | Controlled by `defaultLegendStats` |
| Nested legend | No | Yes (>1 group) | Multiple Group by dimensions required |
| Label truncation | Yes | Yes | |
| Width | Yes | Yes | UI label is "Width", not "Legend size" |

### 5. "<Chart type> examples" section

- 2-4 real-world examples using **Kibana Sample Data**.
- Use **definition list** format with bold example title.
- Structure each example:
  - `* Example based on: <sample data set name>`
  - Configuration keys as bullet points (Slice by, Metric, Style, Legend, etc.)
  - An image of the result, sized with `"=60%"` or `"=70%"`
- Showcase **different features** (e.g., basic config, donut variant, filters, multiple metrics).

## Chart-page-specific formatting

For general syntax, refer to the **docs-syntax-help** skill. These conventions are specific to chart pages:

### Images

- Store at `explore-analyze/images/<image-name>.png`
- Reference with: `![Alt text](/explore-analyze/images/<image-name>.png "=60%")`
- Sizing: `"=50%"` for smaller inline images, `"=60%"` for examples, `"=70%"` for settings screenshots.
- Alt text should be descriptive, not "screenshot".

### Icons

| Icon | Syntax | Usage |
|------|--------|-------|
| Style/brush | `{icon}\`brush\`` | Style settings panel |
| Layer settings | `{icon}\`app_management\`` | Layer settings (9.3+/Serverless) |
| Actions menu | `{icon}\`boxes_horizontal\`` | Layer actions menu (9.0-9.2) |
| Add layer | `{icon}\`plus_in_square\`` | Add layer button |

For the legend icon, use: `![Legend icon](/explore-analyze/images/kibana-legend-icon.svg "")`

### Version-specific UI patterns

When UI differs between versions:

```
* {applies_to}`serverless: ga` {applies_to}`stack: ga 9.3` Select {icon}`app_management` **Layer settings**.
* {applies_to}`stack: ga 9.0-9.2` Select {icon}`boxes_horizontal`, then select **Layer settings**.
```

### Cross-references

- Other chart types: `[bar charts](bar-charts.md)`
- Lens page: `[**Lens**](../lens.md)`
- Lens features: `[Assign colors to terms](../lens.md#assign-colors-to-terms)`
- Sample data: `[sample data](/manage-data/ingest/sample-data.md)`

### Internal links

Link from steps to settings sections:

```
2. Configure the [**Slice by**](#slice-by-settings) dimension.
3. Configure the [**Metric**](#metric-settings) dimension.
```

Link from best practices to advanced scenarios when relevant.

### Variables

Use `{{kib}}` (Kibana), `{{es}}` (Elasticsearch), `{{data-source}}` (data view / data source).

## Checklist

- [ ] Frontmatter has `navigation_title`, `applies_to`, and `description`
- [ ] Hero image exists and is referenced
- [ ] "Build a chart" stepper uses standard Access Lens / Save steps
- [ ] Prerequisites snippet included before the stepper
- [ ] All settings verified against Kibana source code (use lens-chart-settings skill)
- [ ] All settings from the Lens editor are documented in the Settings section
- [ ] Shared snippets included where applicable (not duplicated)
- [ ] Examples use Kibana Sample Data and include images
- [ ] Internal links from steps to settings sections
- [ ] Links from best practices to related advanced scenarios
- [ ] `lens.md` updated to link to the new page
