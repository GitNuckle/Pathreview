## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/148

**Issue title:** Skill extractor fails to detect JavaScript and TypeScript

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
`extract_skills()` in `ingestion/parsers/skill_extractor.py` returns no detections at
all for text that clearly describes JavaScript work, and for TypeScript samples
(mentioning `.tsx`/`.ts` files and the word TypeScript) it detects only `React`.
Python, DevOps, and database detection all work correctly in the same file, so this is
isolated to the JS/TS-specific logic inside `_detect_languages()`. The fix is scoped to
a single file (`skill_extractor.py`) and its corresponding test file, with four
previously-failing tests named directly in the issue: `test_javascript_detection`,
`test_text_with_typescript_files`, `test_devops_tool_detection`, and
`test_docker_compose_detection`.

**Branch name:** fix/148-skill-extractor-js-ts

**Setup confirmation:** [x] App runs locally

**Cohort ledger:** [x] Issue added to cohort ledger

**Note:** Previously claimed and documented issue #130 (Docker memory limits) for
Weeks 7-8, but investigation showed the bug did not reproduce against current main (no
LLM proxy service exists in `docker-compose.yml`, and existing services already had
memory limits configured). Switched to issue # 148 for Week 9 submission since it
reproduces cleanly and is well-scoped to a single file.

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** N/A

**Reproduction notes:**
Ran the issue's two examples directly against `extract_skills()`:
```python
e.extract_skills('Wrote index.js using const arrow functions and async/await callbacks')
# -> [] (matches issue's reported observed output)

[d.name for d in e.extract_skills('Built app.tsx and types.ts with strict TypeScript interfaces')]
# -> ['React'] (matches issue's reported observed output)
```
Both matched the issue's "observed" output exactly, confirming the bug reproduces
cleanly on current main.

Read through `_detect_languages()` line by line to find the actual root cause:
- JS/TS detection is almost entirely gated on a `filename` argument, which is `None`
  in both repro calls.
- The only text-based JS check, `re.search(r"\b(import|require)\s+", text)`, requires
  whitespace after the keyword and neither example uses `import`/`require` at all —
  they use `const`, arrow syntax, and `async`/`await`, none of which are checked
  anywhere in the method.
- `JS_TS_KEYWORDS` is defined as a class attribute but never referenced in the method
  body — dead code, and the actual root cause.
- TypeScript is only ever assigned via `.ts` in `filename`; there's no content-based
  TS signal at all.
- React "detects" on the second example only because `.tsx` is a literal string in
  `REACT_INDICATORS` and happens to appear directly in the input text.

**PLAN.md link:** [https://github.com/GitNuckle/Pathreview/blob/148-skill-extractor/PLAN.md]

**Walkthrough video (recommended):** [not recorded]

**Blockers or open questions:** None — issue reproduces cleanly and root cause is clear from reading the code directly.

## Week 9 — Solution building & PR submission

**Implementation summary:**
Rewrote the JavaScript evidence checks in `_detect_languages()` to look at real syntax
in the text itself (`require(...)` including no-space calls, `import ... from ...`,
`export` statements, arrow function syntax, `async`/`await` usage), plus a literal
"javascript"/`.js`/`.jsx` mention check for plain-text descriptions. Added a fully
independent TypeScript evidence check (`interface` declarations, type annotations,
literal "typescript" mention, `.ts`/`.tsx` mentioned in text) so JavaScript and
TypeScript are detected independently rather than as a mutually exclusive label —
necessary because a real `.tsx` file legitimately has both.

Deliberately avoided switching to raw keyword-membership checks against
`JS_TS_KEYWORDS` (e.g. "does `let` or `class` appear anywhere in the text") after
testing that approach against a plain English sentence ("Let's go to class together")
and confirming it would false-positive. Kept every check structural (regex requiring
real syntax shape) instead.

**Tests added:** 4 new tests in `tests/unit/test_skill_extractor.py` — the issue's two
exact repro examples, a negative test for plain English containing JS/TS keywords, and
a realistic `.tsx` file test expecting both React and TypeScript. Ran all four locally
against the fixed implementation before adding them to the suite — all passed.

**Known limitation found but not fixed (flagged for reviewers):** The pre-existing
Python import check (`re.search(r"\bimport\s+\w+", text)`) also matches JS/TS
`import ... from` statements, since it doesn't check for the trailing `from`. This
predates this PR and is unrelated to # 148, so it was left as-is and noted in the PR
description rather than expanding scope.

**PR link:** [to be added after opening PR]

**Self-review checklist:** [x] `make test-unit` passes for touched files
[ ] `make lint` / `make typecheck` — pass on touched file individually; repo-wide
pre-existing issues unrelated to this change were not addressed, per scope.
