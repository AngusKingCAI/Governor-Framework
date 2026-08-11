# Fix Workflow - Systematic Issue Resolution

This workflow defines the process for addressing issues identified in external reviews, security audits, or quality assessments. It ensures systematic, researched, and user-guided fixes with proper testing and verification.

## Workflow Architecture

The fix workflow uses a **sequential issue-by-issue approach** with research-first decision making:
- Research each issue independently before proposing solutions
- User decision before implementation
- Fix → Test → Verify cycle for each issue
- Final full test suite run before commit
- Git push only after all tests pass

## Phase 1: Issue Triage and Planning

### 1. RECEIVE_FINDINGS
Input source for fix workflow:
- External AI reviews
- Security audit reports
- Compliance assessment findings
- Code quality scan results
- User-reported issues

**Output**: List of issues with severity ratings (P0 Critical, P1 High, P2 Medium, P3 Low)

### 2. CREATE_FIX_PLAN
Create a prioritized fix plan based on:

**Prioritization Criteria**:
- **Security vulnerabilities** (P0): Immediate fix required
- **Compliance violations** (P0): Must fix for regulatory requirements
- **Functional gaps** (P1): High priority for core functionality
- **Code quality issues** (P2): Medium priority, technical debt
- **Documentation issues** (P3): Low priority, cosmetic

**Plan Structure**:
```markdown
## Fix Plan for [Review Name]

### P0 Critical (Must Fix Immediately)
1. Issue Title - Brief description
2. Issue Title - Brief description

### P1 High (High Priority)
3. Issue Title - Brief description
4. Issue Title - Brief description

### P2 Medium (Technical Debt)
5. Issue Title - Brief description

### P3 Low (Nice to Have)
6. Issue Title - Brief description
```

**Exit Condition**: Fix plan created and prioritized.

---

## Phase 2: Systematic Issue Resolution

### 3. PROCESS_ISSUES (Sequential Loop)

For each issue in prioritized order:

#### 3.1 RESEARCH_ISSUE
Research the issue to understand:
- **Technical basis**: What is the underlying technical problem?
- **Best practices**: What do industry standards recommend?
- **Impact assessment**: What is the risk if not fixed?
- **Fix options**: What are the possible solutions?

**Research Methods**:
- Web search for industry best practices
- Cross-reference with ARCHITECTURE.md principles
- Check IMPLEMENTATION.md patterns
- Review SOFTWARE_ENGINEERING_PRINCIPLES.md
- Look at similar code in the repository

**Research Output**: Summary of findings with citations if applicable

#### 3.2 PROPOSE_DECISION
Present research findings and fix options to user using ask_user_question.

**Decision Options**:
- Option A: Implement fix with approach X
- Option B: Implement fix with approach Y
- Option C: Defer/Document as out of scope
- Option D: Skip (user choice)

**Exit Condition**: User selects an option.

#### 3.3 IMPLEMENT_FIX
Implement the fix based on user decision.

**Implementation Requirements**:
- Follow SOFTWARE_ENGINEERING_PRINCIPLES.md
- Maintain zero external dependencies (if applicable)
- Update related documentation if needed
- Add comments explaining the fix rationale

**Implementation Tracking**:
- Use todo_write to track each issue
- Mark issue as "in_progress" when implementing
- Mark issue as "completed" after implementation

#### 3.4 VERIFY_FIX
After implementing each fix:
- Run affected tests if applicable
- Check for compilation/import errors
- Verify fix doesn't break existing functionality

**Exit Condition**: Fix compiles and doesn't cause test failures.

**Iteration Loop**: If fix causes test failures:
- Analyze failure root cause
- Adjust fix as needed
- Re-run tests
- Maximum 3 iterations per fix

---

## Phase 3: Testing and Verification

### 4. RUN_FULL_TEST_SUITE
After all fixes are implemented:
- Run complete test suite: `python -m unittest discover -s Overseer/Tests -p "test_*.py" -v`
- Or direct execution: `python Overseer/Tests/test_overseer.py`

**Test Requirements**:
- ALL tests must pass
- No new test failures introduced
- No compilation errors
- No import errors

**Exit Condition**: 100% test pass rate.

### 5. FIX_TEST_FAILURES (Iteration Loop)
If any tests fail:
- Analyze each failure independently
- Fix implementation or test as needed
- Re-run full test suite
- Maximum 3 iterations per failure type

**Exit Condition**: All tests pass.

---

## Phase 4: Documentation Updates

### 6. UPDATE_DOCUMENTATION
Update relevant documentation based on fixes:

**When to Update Documentation**:
- Changed architectural approach → Update ARCHITECTURE.md
- Changed implementation patterns → Update IMPLEMENTATION.md
- Fixed compliance gaps → Update ORGANIZATIONAL_GUIDE.md
- Changed workflow process → Update WORKFLOW.md
- Added new patterns → Update SOFTWARE_ENGINEERING_PRINCIPLES.md

**Documentation Requirements**:
- Keep document index in AGENTS.md updated
- Ensure consistency across all documents
- Document why changes were made

**Exit Condition**: Documentation reflects current implementation state.

---

## Phase 5: Commit and Push

### 7. CREATE_COMMIT
Create commit with detailed message:

**Commit Message Format**:
```bash
git commit -m "$(cat <<'EOF'
type: brief description of changes

Detailed summary of changes:
- Fix 1: description (Issue #)
- Fix 2: description (Issue #)
- Fix 3: description (Issue #)

Test Results: [number]/[number] tests passing

Generated with [Devin](https://devin.ai)

Co-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>
EOF
)"
```

**Commit Message Guidelines**:
- First line: type + brief description (50 chars or less)
- Body: detailed bullet list of changes
- Include test results
- Use present tense ("fix" not "fixed")
- Reference issue numbers if applicable

### 8. PUSH_TO_GIT
Push changes to remote repository:
```bash
git push origin main
```

**Exit Condition**: Changes successfully pushed to remote.

---

## Phase 6: Workflow Improvement

### 9. DOCUMENT_LESSONS_LEARNED
Identify workflow improvements to prevent future issues:

**Common Workflow Deviations**:
- Skipping test plan creation
- Implementing without testing
- Assuming fixes without verification
- Pushing with failing tests
- Static review claimed as testing

**Prevention Mechanisms**:
- Workflow enforcement in WORKFLOW.md
- Mandatory test plan step
- Mandatory test execution step
- Gate before commit: tests must pass
- Gate before push: commit must be verified

**Update Process**:
- Add workflow deviation patterns to AGENTS.md
- Update WORKFLOW.md with new enforcement steps
- Create checklist for critical phases
- Document anti-patterns to avoid

---

## Issue-by-Issue Tracking Template

For each issue in the fix plan, track:

```markdown
### Issue: [Title]
**Status**: [pending/in_progress/completed]
**Priority**: [P0/P1/P2/P3]
**Research**: [link to research findings or summary]
**Decision**: [user decision with rationale]
**Implementation**: [date implemented, files changed]
**Verification**: [test results]
**Commit**: [commit hash]
```

---

## Exit Criteria

The fix workflow is complete when:
1. All prioritized issues are addressed or documented as deferred
2. All tests pass (100% pass rate)
3. Documentation is updated to reflect changes
4. Changes are committed with detailed message
5. Changes are pushed to remote repository
6. Lessons learned are documented to prevent recurrence

---

## Success Metrics

- **Test Pass Rate**: 100% (all tests must pass)
- **Fix Coverage**: All P0/P1 issues addressed, P2/P3 as prioritized
- **Documentation Accuracy**: All documents reflect current state
- **Git History**: Clean, descriptive commits with proper attribution
- **Workflow Compliance**: No workflow violations in fix process

---

## Anti-Patterns to Avoid

### During Fix Implementation
- ❌ Fixing multiple issues simultaneously without testing
- ❌ Skipping research and jumping to implementation
- ❌ Making changes without user approval
- ❌ Pushing before tests pass
- ❌ Assuming fixes work without verification

### During Testing
- ❌ Running only subset of tests
- ❌ Ignoring test failures
- ❌ Making unverified assumptions about fix correctness
- ❌ Not re-running full suite after changes

### During Documentation
- ❌ Documenting implementation that doesn't match code
- ❌ Forgetting to update document index
- ❌ Documenting assumptions without verification
- ❌ Outdated compliance claims

---

## Example: Fix Workflow Execution

**Context**: External AI review identified 12 issues in overseer.py

**Phase 1**: Created prioritized fix plan with 7 P0/P1 issues, 5 P2/P3 issues

**Phase 2**: Processed each issue sequentially:
1. Research: Websearch for best practices on secret detection patterns
2. Decision: User chose to remove overly broad token pattern
3. Implement: Removed token pattern from SECRET_PATTERNS
4. Verify: Tests still pass
5. Repeat for remaining 11 issues

**Phase 3**: Ran full test suite → 44/44 tests passing

**Phase 4**: Updated WORKFLOW.md with TDD enforcement (prevent future workflow deviations)

**Phase 5**: Created commit: "fix: address external AI review findings..."
Pushed to GitHub: f1f94f9

**Phase 6**: Documented workflow deviation (static review as testing) and added enforcement to WORKFLOW.md

**Result**: All issues addressed, tests passing, code pushed, workflow improved.
