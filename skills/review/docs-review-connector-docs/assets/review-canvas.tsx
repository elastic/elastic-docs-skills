// Template for the draft-selection canvas in Cursor. Don't edit a generated copy by hand:
// scripts/build_canvas.py fills DATA from drafts.json, and scripts/apply_canvas.py reads the
// saved selections and edits back. The state keys used with useCanvasState are part of that
// contract: selected, edits, summaries, events.
import {
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Checkbox,
  DiffStats,
  DiffView,
  Divider,
  Grid,
  H1,
  H2,
  Link,
  Pill,
  Row,
  Select,
  Spacer,
  Stack,
  Stat,
  Table,
  Text,
  TextArea,
  useCanvasState,
  useHostTheme,
} from "cursor/canvas";

type Priority = "P1" | "P2" | "P3";
type Draft = {
  id: string;
  kind: "inline" | "summary" | "reply";
  priority: Priority;
  title: string;
  why: string;
  selected: boolean;
  body: string;
  location: string;
  startLine?: number;
  original?: string;
};
type Check = { area: string; finding: string; status: string };
type PR = {
  number: number;
  title: string;
  author: string;
  head: string;
  status: string;
  summary: string;
  event: string;
  notes: string[];
  checks: Check[];
  drafts: Draft[];
};
type CanvasData = { repo: string; generated: string; prs: PR[] };

const DATA: CanvasData = /*DATA:BEGIN*/ { repo: "elastic/kibana", generated: "", prs: [] } /*DATA:END*/;

const EVENT_OPTIONS = [
  { value: "APPROVE", label: "Approve" },
  { value: "COMMENT", label: "Comment" },
  { value: "REQUEST_CHANGES", label: "Request changes" },
];

const suggestionOf = (body: string): string | null => {
  const m = /```suggestion[^\n]*\n([\s\S]*?)\n?```/.exec(body);
  return m ? m[1] : null;
};

type Token = { text: string; type: "same" | "removed" | "added" };

const wordDiff = (before: string, after: string): Token[] => {
  const a = before.split(/(\s+)/).filter((t) => t !== "");
  const b = after.split(/(\s+)/).filter((t) => t !== "");
  if (a.length * b.length > 400000) return [{ text: after, type: "added" }];
  const dp: number[][] = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
  for (let i = a.length - 1; i >= 0; i--)
    for (let j = b.length - 1; j >= 0; j--)
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const out: Token[] = [];
  const push = (text: string, type: Token["type"]) => {
    const last = out[out.length - 1];
    if (last && last.type === type) last.text += text;
    else out.push({ text, type });
  };
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) {
      push(a[i], "same");
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) push(a[i++], "removed");
    else push(b[j++], "added");
  }
  while (i < a.length) push(a[i++], "removed");
  while (j < b.length) push(b[j++], "added");
  return out;
};

function SuggestionDiff({ draft, body }: { draft: Draft; body: string }) {
  const theme = useHostTheme();
  if (draft.original === undefined || draft.startLine === undefined) return null;
  const start = draft.startLine;
  const before = draft.original.split("\n");
  const suggestion = suggestionOf(body);

  if (suggestion === null) {
    return (
      <Stack gap={4}>
        <Text size="small" tone="tertiary">Comment on this line, no suggestion</Text>
        <Card>
          <CardBody style={{ padding: 0 }}>
            <DiffView
              lines={before.map((content, i) => ({ type: "unchanged" as const, content, lineNumber: start + i }))}
              style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
            />
          </CardBody>
        </Card>
      </Stack>
    );
  }

  const after = suggestion === "" ? [] : suggestion.split("\n");
  return (
    <Stack gap={6}>
      <Card>
        <CardHeader trailing={<DiffStats additions={after.length} deletions={before.length} />}>
          <Text size="small" style={{ fontFamily: "monospace" }}>{`Suggested change · ${draft.location}`}</Text>
        </CardHeader>
        <CardBody style={{ padding: 0 }}>
          <DiffView
            lines={[
              ...before.map((content, i) => ({ type: "removed" as const, content, lineNumber: start + i })),
              ...after.map((content, i) => ({ type: "added" as const, content, lineNumber: start + i })),
            ]}
            style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
          />
        </CardBody>
      </Card>
      {suggestion === draft.original && (
        <Text size="small" tone="secondary">The suggestion matches the current lines, so it changes nothing.</Text>
      )}
      {after.length > 0 && suggestion !== draft.original && (
        <Stack gap={4}>
          <Text size="small" tone="tertiary">Changed words</Text>
          <div
            style={{
              fontFamily: "monospace",
              fontSize: 12,
              lineHeight: 1.7,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              padding: "8px 10px",
              borderRadius: 4,
              border: `1px solid ${theme.stroke.tertiary}`,
            }}
          >
            {wordDiff(draft.original, suggestion).map((t, i) =>
              t.type === "same" ? (
                <span key={i}>{t.text}</span>
              ) : (
                <span
                  key={i}
                  style={{
                    background: t.type === "removed" ? theme.diff.removedLine : theme.diff.insertedLine,
                    textDecoration: t.type === "removed" ? "line-through" : undefined,
                    borderRadius: 2,
                  }}
                >
                  {t.text}
                </span>
              )
            )}
          </div>
        </Stack>
      )}
    </Stack>
  );
}

const KIND_LABEL: Record<Draft["kind"], string> = {
  inline: "inline",
  summary: "added to the summary",
  reply: "thread reply",
};

export default function ConnectorDocsReview() {
  const theme = useHostTheme();
  const [tab, setTab] = useCanvasState<string>("tab", String(DATA.prs[0]?.number ?? ""));
  const [selected, setSelected] = useCanvasState<Record<string, boolean>>("selected", {});
  const [edits, setEdits] = useCanvasState<Record<string, string>>("edits", {});
  const [summaries, setSummaries] = useCanvasState<Record<string, string>>("summaries", {});
  const [events, setEvents] = useCanvasState<Record<string, string>>("events", {});
  const [open, setOpen] = useCanvasState<Record<string, boolean>>("open", {});
  const [filter, setFilter] = useCanvasState<string>("filter", "all");

  const isOn = (d: Draft) => selected[d.id] ?? d.selected;
  const isOpen = (d: Draft) => open[d.id] ?? d.priority !== "P3";
  const bodyOf = (d: Draft) => edits[d.id] ?? d.body;

  const all = DATA.prs.flatMap((p) => p.drafts);
  const onCount = all.filter(isOn).length;
  const urgent = all.filter((d) => d.priority !== "P3" && isOn(d)).length;
  const pr = DATA.prs.find((p) => String(p.number) === tab) ?? DATA.prs[0];
  if (!pr) return null;
  const visible = pr.drafts.filter((d) => filter === "all" || d.priority === filter);
  const priorities = (["P1", "P2", "P3"] as Priority[]).filter((p) => pr.drafts.some((d) => d.priority === p));

  return (
    <Stack gap={20} style={{ padding: 4 }}>
      <Stack gap={6}>
        <H1>{`Connector docs review: ${DATA.prs.map((p) => `#${p.number}`).join(", ")}`}</H1>
        <Text tone="secondary">
          Draft review comments in your voice. Nothing is posted. Select or edit drafts here, then tell the agent in chat to
          post the selection. The agent copies your choices back into drafts.json and shows you the exact payload first.
        </Text>
      </Stack>

      <Row gap={24}>
        <Stat value={String(all.length)} label="Drafts" />
        <Stat value={String(onCount)} label="Selected" />
        <Stat value={String(urgent)} label="Selected P1 or P2" />
        <Stat value={String(Object.keys(edits).length)} label="Edited by you" />
      </Row>

      {DATA.prs.length > 1 && (
        <Row gap={8} wrap>
          {DATA.prs.map((p) => (
            <Pill key={p.number} active={p.number === pr.number} onClick={() => setTab(String(p.number))}>
              {`#${p.number} (${p.drafts.filter(isOn).length}/${p.drafts.length})`}
            </Pill>
          ))}
        </Row>
      )}

      <Stack gap={8}>
        <H2>{`#${pr.number} ${pr.title}`}</H2>
        <Text size="small" tone="secondary">{[pr.author && `by ${pr.author}`, pr.status].filter(Boolean).join(" · ")}</Text>
        <Row gap={12}>
          <Link href={`https://github.com/${DATA.repo}/pull/${pr.number}`}>Open the PR on GitHub</Link>
          <Link href={`https://github.com/${DATA.repo}/pull/${pr.number}/files`}>Files changed</Link>
        </Row>
      </Stack>

      {pr.notes.map((n, i) => (
        <Callout key={i} tone="warning" title="Before posting">
          {n}
        </Callout>
      ))}

      <Card>
        <CardHeader trailing={<Text size="small" tone="tertiary">posted as the review body</Text>}>Review summary</CardHeader>
        <CardBody>
          <Grid columns="1fr 180px" gap={12} align="start">
            <TextArea
              value={summaries[pr.number] ?? pr.summary}
              onChange={(v) => setSummaries((s) => ({ ...s, [pr.number]: v }))}
              rows={Math.min(8, Math.max(2, Math.ceil((summaries[pr.number] ?? pr.summary).length / 90) + 1))}
            />
            <Stack gap={6}>
              <Text size="small" tone="secondary">Review event</Text>
              <Select
                value={events[pr.number] ?? pr.event}
                onChange={(v) => setEvents((e) => ({ ...e, [pr.number]: v }))}
                options={EVENT_OPTIONS}
              />
            </Stack>
          </Grid>
        </CardBody>
      </Card>

      {pr.drafts.length > 0 && (
        <Stack gap={12}>
          <Row gap={8} align="center">
            <H2>Drafts</H2>
            <Spacer />
            {priorities.length > 1 &&
              ["all", ...priorities].map((f) => (
                <Pill key={f} size="sm" active={filter === f} onClick={() => setFilter(f)}>
                  {f === "all" ? "All" : f}
                </Pill>
              ))}
            <Button
              variant="ghost"
              onClick={() => setSelected((s) => ({ ...s, ...Object.fromEntries(pr.drafts.map((d) => [d.id, true])) }))}
            >
              Select all
            </Button>
            <Button
              variant="ghost"
              onClick={() => setSelected((s) => ({ ...s, ...Object.fromEntries(pr.drafts.map((d) => [d.id, false])) }))}
            >
              Clear
            </Button>
          </Row>
          {visible.map((d) => {
            const on = isOn(d);
            const expanded = isOpen(d);
            const edited = edits[d.id] !== undefined;
            return (
              <Stack
                key={d.id}
                gap={8}
                style={{
                  padding: 12,
                  borderRadius: 6,
                  border: `1px solid ${theme.stroke.tertiary}`,
                  background: on ? theme.bg.editor : theme.fill.quaternary,
                  opacity: on ? 1 : 0.75,
                }}
              >
                <Row gap={10} align="center">
                  <Checkbox checked={on} onChange={(v) => setSelected((s) => ({ ...s, [d.id]: v }))} />
                  <Pill size="sm" active={d.priority !== "P3"}>{d.priority}</Pill>
                  <Text weight="semibold">{d.title}</Text>
                  {edited && <Text size="small" tone="tertiary">edited</Text>}
                  <Spacer />
                  <Text size="small" tone="tertiary" style={{ fontFamily: "monospace" }}>
                    {d.kind === "inline" ? d.location : KIND_LABEL[d.kind]}
                  </Text>
                  <Button variant="ghost" onClick={() => setOpen((o) => ({ ...o, [d.id]: !expanded }))}>
                    {expanded ? "Hide" : "Show"}
                  </Button>
                </Row>
                {expanded && (
                  <Stack gap={6}>
                    {d.why && <Text size="small" tone="secondary">{`Why (not posted): ${d.why}`}</Text>}
                    {d.kind === "reply" && <Text size="small" tone="tertiary">{d.location}</Text>}
                    <SuggestionDiff draft={d} body={bodyOf(d)} />
                    <Row gap={8} align="center">
                      <Text size="small" tone="tertiary">Text as posted</Text>
                      <Spacer />
                      {edited && (
                        <Button
                          variant="ghost"
                          onClick={() =>
                            setEdits((e) => {
                              const next = { ...e };
                              delete next[d.id];
                              return next;
                            })
                          }
                        >
                          Reset to draft
                        </Button>
                      )}
                    </Row>
                    <TextArea
                      value={bodyOf(d)}
                      onChange={(v) => setEdits((e) => ({ ...e, [d.id]: v }))}
                      rows={Math.min(12, bodyOf(d).split("\n").length + 2)}
                      style={{ fontFamily: "monospace", fontSize: 12 }}
                    />
                  </Stack>
                )}
              </Stack>
            );
          })}
        </Stack>
      )}

      {pr.checks.length > 0 && (
        <Stack gap={10}>
          <H2>Checks</H2>
          <Table
            headers={["Area", "Finding", "Status"]}
            rows={pr.checks.map((c) => [c.area, c.finding, c.status])}
            columnAlign={["left", "left", "left"]}
          />
        </Stack>
      )}

      <Divider />

      <Stack gap={10}>
        <H2>What would be posted</H2>
        <Table
          headers={["PR", "Event", "Inline", "Summary additions", "Replies"]}
          rows={DATA.prs.map((p) => {
            const on = p.drafts.filter(isOn);
            const count = (k: Draft["kind"]) => String(on.filter((d) => d.kind === k).length);
            return [
              `#${p.number}`,
              EVENT_OPTIONS.find((o) => o.value === (events[p.number] ?? p.event))?.label ?? p.event,
              count("inline"),
              count("summary"),
              count("reply"),
            ];
          })}
          columnAlign={["left", "left", "right", "right", "right"]}
        />
        <Text size="small" tone="tertiary">
          {`Lines read at each PR head on ${DATA.generated}: ${DATA.prs.map((p) => `#${p.number} at ${p.head.slice(0, 7)}`).join(", ")}. If a head moves before you post, the agent re-checks every anchor first.`}
        </Text>
      </Stack>
    </Stack>
  );
}
