# Research Workflow - Documentation Refinement Through Iterative Research

This workflow defines the process for systematically researching and refining Overseer documentation to the point where implementation is straightforward and unambiguous. The goal is to make documentation so well-defined that AI implementation becomes nearly foolproof.

## Workflow Philosophy

**Documentation-First Approach**: Research and refine documentation until it's implementation-ready, then implement.

**One-Decision-at-a-Time**: Research ONE aspect at a time, present findings, get user decision, then proceed to next aspect. No comprehensive dumps.

**Hyper-Specific Research**: Research down to the function and parameter level, not just high-level concepts.

**User-Guided Iteration**: Research → Present → Decide → Refine cycle until documentation is solid.

**No Implementation Yet**: This workflow focuses ONLY on documentation research and refinement. Implementation happens separately after documentation is complete.

**Actionability Over Comprehensiveness**: If the user can read the first paragraph and know what to do, the research succeeds. If they need to read everything to understand, it fails.

## Workflow Architecture

The research workflow uses a **continuous research loop** with user decision-making:
- Research specific implementation aspects (down to function level)
- Present findings to user with implementation implications
- User decides: accept, reject, modify, or defer
- Refine documentation based on decisions
- Repeat until documentation is implementation-ready

## Phase 1: Research Scope Definition

### 1. DEFINE_RESEARCH_AREAS
Identify documentation areas that need refinement:

**Research Priorities**:
- **Module interfaces**: Function signatures, parameters, return types
- **Data structures**: Class definitions, field types, validation rules
- **Error handling**: Exception types, error propagation, fail-closed behavior
- **Logging specifics**: Log format, log levels, log file structure
- **State management**: State transitions, persistence, invalidation
- **Performance**: Caching strategies, optimization points, latency targets
- **Security**: Input validation, secret handling, access control

**Research Scope Template**:
```markdown
## Research Scope for [Module/Aspect]

### Functions to Research
- function_name(): purpose, parameters, return type, error handling
- function_name(): purpose, parameters, return type, error handling

### Data Structures to Research
- ClassName: fields, validation, serialization
- ClassName: fields, validation, serialization

### Cross-Module Interfaces
- Module A → Module B: data flow, error handling, logging
- Module B → Module C: data flow, error handling, logging
```

**Exit Condition**: Research scope defined with specific functions/data structures to research.

---

## Phase 2: Continuous Research Loop

### 2. RESEARCH_ASPECT (Loop)

For each function, data structure, or interface in scope:

#### 2.1 HYPER-SPECIFIC_RESEARCH
Research the specific implementation aspect down to function level.

**Research Output**: Individual findings that can be presented one at a time.

#### 2.2 PRESENT_ONE_FINDING
Present ONE research finding at a time with simple explanations.

**Presentation Format**:
```markdown
## Research Aspect #[N] of [Total]: [Aspect Name]

**Progress**: ████░░░░░░ [X]% (completed findings of total findings)

### Finding #[F]: [Finding Title]

**What the research found:**
[Simple, one-sentence explanation of what was found]

**What this means:**
[Simple explanation of what this implies in practice]

**Benefits:**
- ✅ [Benefit 1]
- ✅ [Benefit 2]

**Downsides:**
- ❌ [Downside 1]
- ❌ [Downside 2]

**Alternative rejected:**
[What alternative was considered and why it was rejected]
```

**Key Principles:**
- **One finding per decision**: Never present multiple findings together
- **Simple language**: Avoid jargon, explain technical terms
- **Clear trade-offs**: Benefits and downsides must be understandable
- **Actionable**: User must be able to decide after reading

#### 2.3 USER_DECISION
Use ask_user_question to get user decision on this specific finding.

**Decision Options:**
- **Accept this finding** - Implement this approach
- **Reject this finding** - Use a different approach
- **Need more explanation** - Get more details before deciding

**Exit Condition**: User selects an option.

#### 2.4 RECORD_DECISION
Record the user's decision and move to next finding.

**Decision Tracking:**
- Document the decision made
- Reason for decision (if provided)
- Move to next finding in queue
- Show progress update

**Exit Condition**: Decision recorded, next finding ready to present.

---

## Phase 3: Documentation Validation

### 3. CROSS-CHECK_DOCUMENTS
After research loop completes, validate consistency across all documents:

**Validation Checklist**:
- ARCHITECTURE.md principles align with MODULE_SPECIFICATIONS.md details
- IMPLEMENTATION.md examples match MODULE_SPECIFICATIONS.md specifications
- No contradictions between documents
- No missing implementation details
- All module interfaces are fully specified
- All data structures are fully defined
- All error handling is specified
- All logging is specified

**Validation Method**:
- Use subagent to cross-check documents
- Identify inconsistencies
- Report findings to user
- Fix inconsistencies based on user decision

**Exit Condition**: All documents are consistent and complete.

---

## Phase 4: Implementation Readiness Assessment

### 4. ASSESS_IMPLEMENTATION_READINESS
Determine if documentation is ready for implementation:

**Readiness Criteria**:
- Every function has clear signature (parameters, return type)
- Every data structure has clear definition (fields, types, validation)
- Every interface has clear contract (input, output, errors)
- Every error case has clear handling (exception type, propagation)
- Every logging point has clear specification (what, when, format)
- Every performance consideration is documented
- Every security consideration is documented
- Testing approach is specified for each component

**Readiness Scoring**:
- **100% Ready**: All criteria met, can implement directly
- **80% Ready**: Minor gaps, can implement with reasonable assumptions
- **60% Ready**: Some gaps, need more research
- **40% Ready**: Major gaps, significant research needed
- **<40% Ready**: Not ready for implementation

**Exit Condition**: Readiness score ≥ 80%, or return to research loop for gaps.

---

## Phase 5: Documentation Completion

### 5. FINALIZE_DOCUMENTATION
When documentation is implementation-ready:

**Final Checklist**:
- MODULE_SPECIFICATIONS.md is complete with function-level details
- ARCHITECTURE.md reflects all architectural decisions
- IMPLEMENTATION.md has code examples for all patterns
- AGENTS.md document index is accurate
- No contradictions or ambiguities
- All cross-references are accurate
- All principles are reflected in specifications

**Final Actions**:
- Commit documentation updates
- Create summary of documentation state
- Mark documentation as "implementation-ready"

**Exit Condition**: Documentation committed and marked as implementation-ready.

---

## Research Aspect Examples

### Example 1: Function-Level Research
**Research Aspect**: `Core/overseer.py` - adapter loading mechanism

**Research Questions**:
- How to dynamically load adapter based on config.json?
- What stdlib modules to use (importlib, importlib.util)?
- How to handle import errors?
- How to cache loaded adapter?
- How to detect config changes and reload?
- What to log during adapter loading?
- How to test adapter loading?

**Documentation Updates**:
- Add to MODULE_SPECIFICATIONS.md Core/overseer.py:
  - Function signature: `load_adapter(config_path: str) -> BaseAdapter`
  - Parameters: config_path with validation
  - Return type: BaseAdapter instance
  - Exceptions: FileNotFoundError, ImportError, ValueError
  - Logging: log which adapter loaded, load time, errors
  - Caching: cache loaded adapter to temporary file
  - Config change detection: file modification time comparison

### Example 2: Data Structure Research
**Research Aspect**: `Core/protocol/models.py` - CanonicalPayload definition

**Research Questions**:
- What fields should CanonicalPayload have?
- What types for each field?
- Which fields are required vs optional?
- How to validate CanonicalPayload?
- How to extend CanonicalPayload for future needs?
- How to serialize CanonicalPayload?
- What logging for CanonicalPayload operations?

**Documentation Updates**:
- Add to MODULE_SPECIFICATIONS.md Core/protocol/models.py:
  - CanonicalPayload dataclass definition
  - All fields with types: action_type (ActionType enum), agent_identity (str), resource (str), access_level (AccessLevel enum), audit_context (dict), metadata (dict, optional), delegation_chain (list, optional)
  - Validation rules: required fields, enum values, field constraints
  - Serialization: to_dict(), from_dict() methods
  - Extensibility: optional metadata field
  - Logging: log creation, validation, serialization

### Example 3: Interface Research
**Research Aspect**: `Core/overseer.py` → `Core/engine/evaluator.py` interface

**Research Questions**:
- What data does overseer.py pass to evaluator?
- What data does evaluator return to overseer?
- How to handle evaluator errors?
- What to log for evaluation calls?
- How to test this interface?

**Documentation Updates**:
- Add to MODULE_SPECIFICATIONS.md both modules:
  - overseer.py: calls `evaluator.evaluate(payload: CanonicalPayload) -> GovernanceDecision`
  - evaluator.py: receives `CanonicalPayload`, returns `GovernanceDecision`
  - Error handling: evaluator raises PolicyEvaluationError, overseer logs and returns deny
  - Logging: overseer logs evaluation call, evaluator logs evaluation details
  - Testing: mock evaluator in overseer tests, mock overseer in evaluator tests

---

## Exit Criteria

The research workflow is complete when:
1. All research aspects are investigated to function-level detail
2. All documentation is updated with specific implementation details
3. All documents are cross-checked for consistency
4. Implementation readiness score ≥ 80%
5. Documentation is committed and marked as implementation-ready
6. No ambiguities or gaps remain that would confuse implementation

---

## Success Metrics

- **Documentation Completeness**: 100% of functions have detailed specifications
- **Documentation Specificity**: All specifications are function-level, not high-level
- **Document Consistency**: 0 contradictions between documents
- **Implementation Readiness**: ≥ 80% readiness score
- **User Decision Rate**: ≥ 80% of research decisions accepted (indicates good research quality)

---

## Anti-Patterns to Avoid

### During Research
- ❌ Researching at high level only (no function details)
- ❌ Skipping research and jumping to documentation updates
- ❌ Making assumptions without verification
- ❌ Not considering security/performance implications
- ❌ Not considering error handling

### During Documentation Updates
- ❌ Adding vague descriptions
- ❌ Not specifying function signatures
- ❌ Not specifying error handling
- ❌ Not specifying logging
- ❌ Creating contradictions with existing documentation

### During Validation
- ❌ Skipping cross-document validation
- ❌ Ignoring inconsistencies found
- ❌ Proceeding to implementation with <80% readiness
- ❌ Not getting user sign-off on readiness

---

## Example: Research Workflow Execution

**Context**: MODULE_SPECIFICATIONS.md needs function-level details for Core/overseer.py

**Phase 1**: Define research scope - adapter loading, config reading, caching mechanism

**Phase 2**: Research loop:
1. Research adapter loading: importlib.import_module pattern recommended
2. Present findings with code example
3. User decision: Accept, add to MODULE_SPECIFICATIONS.md
4. Update MODULE_SPECIFICATIONS.md with `load_adapter()` function signature
5. Repeat for config reading, caching mechanism

**Phase 3**: Cross-check documents - MODULE_SPECIFICATIONS.md vs ARCHITECTURE.md - consistent

**Phase 4**: Assess readiness - 85% ready (minor gaps in error handling)

**Phase 5**: Return to research loop for error handling gaps, update documentation

**Final**: MODULE_SPECIFICATIONS.md has complete function-level details, 95% readiness, committed

**Result**: Documentation is implementation-ready, can proceed to actual implementation with minimal ambiguity.

---

## Research Loop Template

For each research aspect, track:

```markdown
### Research Aspect: [Function/Structure]
**Status**: [pending/researching/presented/accepted/rejected/deferred]
**Module**: [module name]
**Aspect Type**: [function/data structure/interface]
**Research Findings**: [summary or link]
**User Decision**: [decision with rationale]
**Documentation Updates**: [files changed, sections added]
**Date Completed**: [date]
```
