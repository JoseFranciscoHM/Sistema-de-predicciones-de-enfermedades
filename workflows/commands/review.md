# Command: /review

> **Purpose:** Validate implementation against all quality gates and rules.
> **Trigger:** Automatically after each task in `/implement`, or manually.

---

## Execution Steps

### Step 1: Determine Applicable Gates

Read `rules/quality-gates.json` and filter gates where `language` matches
an entry in `environment.tech_stack` from `harness-config.yaml`, or where
`language` is `"all"`.

### Step 2: Execute Quality Gates

For each applicable gate in `pre_commit`:

1. **Substitute placeholders** in the command (`{source_files}`, `{project}`, etc.)
2. **Run the command**
3. **Record result:** PASS or FAIL with output

If `command` fails because the tool is not installed, try `command_alt`.

### Step 3: Self-Review Checklist

The agent checks the code against:

- [ ] `rules/coding-standards.md` — naming, formatting, documentation
- [ ] `rules/security-rules.md` — active profile rules
- [ ] `constitution.md` — non-negotiable principles
- [ ] Task `_Boundary_` — code stays within scope
- [ ] No hardcoded secrets, debug prints, or dead code

### Step 4: Handle Results

| Result | Action |
|--------|--------|
| ✅ All gates pass + self-review clean | Mark task complete |
| ❌ Gate fails (attempt 1) | Fix issue, re-run failed gate |
| ❌ Gate fails (attempt 2) | Fix issue, re-run one more time |
| 🛑 Gate fails (attempt 3) | **STOP.** Pause and request human guidance |

### Step 5: Report

```
📊 Review Results for TASK-XX:

Quality Gates:
  ✅ QG-01: Test coverage (87%) — PASS
  ✅ QG-02: Ruff linter — PASS
  ⚠️ QG-03: mypy type check — WARNING (optional)

Self-Review:
  ✅ Coding standards — compliant
  ✅ Security rules — compliant
  ✅ Boundary respected

Result: PASS ✅ | FAIL ❌ | BLOCKED 🛑
```

---

## Pre-Merge Review

When all tasks are complete, the agent runs `pre_merge` gates:

- **QG-50:** Plan approved by human ✓
- **QG-51:** All tasks completed ✓
- **QG-52:** Decision log updated ✓

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Quality gate tool not installed | Try `command_alt`, warn if unavailable |
| Mandatory gate fails 3x | Pause, present diagnosis, ask human |
| Optional gate fails | Log warning, continue |
| Self-review finds violation | Fix before running gates |
