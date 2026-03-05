# Eval Schemas

JSON schemas used by the skill evaluation system.

## evals.json

Located at `<skill-dir>/evals/evals.json`.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample.txt"],
      "expectations": [
        "The output includes X",
        "The skill used Y approach"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Must match the skill's frontmatter `name`
- `evals[].id`: Unique integer
- `evals[].prompt`: Realistic user prompt (substantive, not trivial)
- `evals[].expected_output`: Human-readable success description
- `evals[].files`: Optional input files (relative to skill root)
- `evals[].expectations`: Verifiable assertions for automated grading

## grading.json

Output from the grader agent.

```json
{
  "expectations": [
    { "text": "assertion text", "passed": true, "evidence": "specific quote" }
  ],
  "summary": { "passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67 },
  "eval_feedback": {
    "suggestions": [{ "assertion": "...", "reason": "..." }],
    "overall": "Brief assessment"
  }
}
```

## comparison.json

Output from blind comparator.

```json
{
  "winner": "A",
  "reasoning": "Why the winner was chosen",
  "rubric": {
    "A": { "content_score": 4.7, "structure_score": 4.3, "overall_score": 9.0 },
    "B": { "content_score": 2.7, "structure_score": 2.7, "overall_score": 5.4 }
  }
}
```

## Writing Good Evals

- **Prompts should be realistic**: Include file paths, personal context, specifics. Not abstract requests.
- **Expectations should be discriminating**: They should fail when the skill doesn't work, not just pass for any output.
- **3-4 evals per skill minimum**: Cover the core use case, an edge case, a validation/error scenario, and a negative case.
- **Focus on what matters**: Test the skill's unique value-add, not things the base model already handles.
- **Always include negative evals**: At least one eval should test input where the skill should produce no findings, no output, or decline to act. Use "Does NOT flag/generate/suggest X" expectations. Without negative evals, skills drift toward over-triggering — one-sided evals create one-sided optimization.
