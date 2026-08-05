# Fix #148: Skill extractor fails to detect JavaScript and TypeScript

## Summary
`extract_skills()` detected no languages for plain-text JavaScript
descriptions, and only detected React (never TypeScript) for TypeScript
descriptions. Root cause: JS/TS detection in `_detect_languages()` was
almost entirely dependent on a `filename` argument that's often not
available, the one text-based check required whitespace after
`import`/`require` (missing `require('fs')`), and export/arrow-function/
async-await syntax were never checked at all despite `JS_TS_KEYWORDS`
existing as dead, unused data. TypeScript had no content-based signal
whatsoever — it only ever came from `.ts` in the filename.

Close # 148

## Changes
- Rewrote the JavaScript evidence checks in `_detect_languages()` to look
  at real syntax in the text itself: `require(...)` (including no-space
  calls), `import ... from ...`, `export` statements, arrow function
  syntax, and `async`/`await` usage — plus a literal "javascript" /
  `.js`/`.jsx` mention check for plain-text descriptions.
- Added a fully independent TypeScript evidence check: `interface`
  declarations, type annotations (`: string`, `: number`, etc.), literal
  "typescript" mention, and `.ts`/`.tsx` mentioned in text.
- JavaScript and TypeScript are now detected independently rather than as
  a mutually exclusive either/or label, so a real `.tsx` file correctly
  produces both.
- Added 4 tests to `tests/unit/test_skill_extractor.py`: the issue's two
  exact examples, a negative test guarding against plain-English false
  positives (e.g. "let's go to class"), and a realistic `.tsx` file test
  expecting both React and TypeScript.

## Testing
- [x] Unit tests pass (`make test-unit`) — all 4 new tests pass locally
- [ ] Integration tests — not run; this is a unit-level fix
- [ ] Linter (`make lint`) — the touched file passes on its own
- [ ] Type checker (`make typecheck`) — the touched file passes on its own
- [x] New/updated tests cover the changes

To verify directly:
```bash
python3 -c "
from ingestion.parsers.skill_extractor import SkillExtractor
e = SkillExtractor()
print([d.name for d in e.extract_skills('Wrote index.js using const arrow functions and async/await callbacks')])
print([d.name for d in e.extract_skills('Built app.tsx and types.ts with strict TypeScript interfaces')])
"
```
Before: `[]` and `['React']`. After: `['JavaScript']` and
`['TypeScript', 'React']`.

## Notes for Reviewers
While testing, I noticed the pre-existing Python import check
(`re.search(r"\bimport\s+\w+", text)`) also matches JS/TS `import ... from`
statements, since it doesn't check for the trailing `from`. This predates
this PR and is unrelated to # 148, so I left it as-is and am flagging it
here rather than expanding scope.
