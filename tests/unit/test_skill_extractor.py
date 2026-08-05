# Add these test methods inside the existing TestSkillExtractor class in
# tests/unit/test_skill_extractor.py. They assume `self.extractor` (or your
# fixture's equivalent) is a SkillExtractor instance — match whatever
# fixture pattern the existing tests already use.

def test_issue_148_javascript_description(self):
    """Issue #148 repro case 1: plain-text JS description with no filename."""
    extractor = SkillExtractor()
    results = extractor.extract_skills(
        "Wrote index.js using const arrow functions and async/await callbacks"
    )
    names = [d.name for d in results]
    assert "JavaScript" in names

def test_issue_148_typescript_description(self):
    """Issue #148 repro case 2: plain-text TS description with no filename."""
    extractor = SkillExtractor()
    results = extractor.extract_skills(
        "Built app.tsx and types.ts with strict TypeScript interfaces"
    )
    names = [d.name for d in results]
    assert "TypeScript" in names
    assert "React" in names

def test_plain_english_not_flagged_as_code(self):
    """Sentences that happen to contain JS/TS keywords as plain English
    words (e.g. 'class', 'let') should not be detected as JavaScript or
    TypeScript."""
    extractor = SkillExtractor()
    results = extractor.extract_skills(
        "Let's go to class together after we var out for a bit."
    )
    names = [d.name for d in results]
    assert "JavaScript" not in names
    assert "TypeScript" not in names

def test_tsx_file_detects_react_and_typescript(self):
    """A real .tsx file with hooks and typed props should detect both
    React and TypeScript, not just one or the other."""
    extractor = SkillExtractor()
    code = """
    import React, { useState } from 'react';

    interface Props {
        label: string;
    }

    export const Counter = ({ label }: Props) => {
        const [count, setCount] = useState<number>(0);
        return null;
    };
    """
    results = extractor.extract_skills(code, filename="Counter.tsx")
    names = [d.name for d in results]
    assert "React" in names
    assert "TypeScript" in names