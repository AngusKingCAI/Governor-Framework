# Governor Framework - Claude Instructions

## Token Efficiency Rules

**Always confirm file paths before reading:** Before reading any file, ask Claude to confirm the exact path to avoid wasted reads on wrong files.

**Be specific and concise:** Use short, direct prompts. Long descriptive prompts waste tokens without adding value.

**Read before write:** Always check if a file exists before attempting to write or modify it.

**Use file lists for operations:** When working with multiple files, list them all in one prompt rather than asking about files individually.

**Batch related changes:** Group related operations into single prompts to reduce conversation overhead.

**Avoid unnecessary exploration:** Don't ask Claude to explore the codebase unless specifically needed for the current task.

**Use targeted reads:** Read only the specific sections of files needed, not entire files unless necessary.

## Architecture Understanding

**Layered System Design:** Governor Framework uses a 7-layer architecture:

1. **Layer 1 - Entry Point (`governor.py`)**: 
   - Minimal logic, only routing
   - Own isolated logging
   - Imports protocol.py ONLY
   - Receives hook events, routes to handlers

2. **Layer 2 - Hook Handlers (`hook_handlers/`)**:
   - Base handler class in `_base.py`
   - Specific handlers for each hook event
   - Each handler implements execute(payload, state_machine, engine)
   - Should be abstracted and follow consistent patterns

3. **Layer 3 - State Machine (`state_machine.py`)**:
   - Self-contained, NO imports from other Governor files
   - Phase-based compliance (INIT, EXECUTE, RESEARCH, PLAN, VALIDATE, COMMIT)
   - Compliance state machine (testing_in_progress, testing_complete, blocked, ready_to_proceed)
   - Bypass management, counter tracking, flag management
   - Agent discovery from .devin/agents.json
   - File locking for state persistence

4. **Layer 4 - Engine (`engine.py`)**:
   - Rule evaluation engine
   - Policy enforcement
   - Action execution

5. **Layer 5 - Actions (`actions/`)**:
   - Specific governance actions
   - Base action class in `_base.py`
   - Should be modular and reusable

6. **Layer 6 - Protocol (`protocol.py`)**:
   - Response format definitions
   - Hook response building functions

7. **Layer 7 - Audit (`audit_log.py`)**:
   - Comprehensive logging of governance decisions

**Key Architectural Principle:** Each layer should be independent with minimal coupling. No layer should import from other Governor files except as specifically documented.

**Current Design Concerns:**
- State machine compliance tracking may not be working as intended
- Layer boundaries may have violations
- CLI-agnostic support needs to be added

## Testing-First Approach

**Never implement without a test plan:** Before making any changes, create a test plan to verify the change works correctly.

**Test in this order:**
1. Implement component
2. Write test to verify functionality
3. Run test
4. Fix any issues
5. Only then move to next component

**Focus on one layer at a time:** Don't try to fix multiple layers simultaneously. Complete and test one layer before moving to the next.

**Verification methods:**
- For CLI detection: Test with different environment variables and filesystem patterns
- For providers: Test event name normalization and format conversion with sample data
- For config generator: Verify generated JSON matches official CLI documentation
- For state machine: Test state transitions and compliance logic

**Test commands to use:**
- `python -c "from Governor.cli.detectors.detector import detect_cli; print(detect_cli())"`
- `python -c "from Governor.cli.providers.<provider> import <Provider>; print(<Provider>('cli', {}).normalize_event('SessionStart'))"`
- `python Governor/setup.py` (for installation testing)

## Project Structure

```
Governor/
├── __init__.py
├── governor.py (entry point)
├── state_machine.py (compliance state)
├── engine.py (rule evaluation)
├── protocol.py (response formats)
├── audit_log.py (logging)
├── hook_handlers/ (hook implementations)
├── actions/ (governance actions)
├── rules/ (YAML rule files)
├── templates/ (rule templates)
├── state/ (runtime state storage)
└── logs/ (execution logs)
```

## Current Project State

**Initial commit:** Currently at initial commit (184ddd7) with basic Governor Framework structure.

**No build process:** This is a Python framework with no compilation step.

**Current focus:** Establishing proper testing procedures before implementing new features.

## Working Style

**Plan before implement:** Always ask Claude to describe its approach before making changes. Wait for approval before proceeding.

**Small incremental changes:** Make small, testable changes rather than large refactors.

**Verify each change:** After each modification, consider how to verify it works correctly before moving on.

**Focus on layer boundaries:** When implementing, ensure you're not violating the stated architectural principles about layer independence.

**Ask for clarification:** If instructions are ambiguous or if you see multiple approaches, present them for decision rather than assuming.

**Flag architectural violations:** If you see code that violates the stated layer boundaries or coupling rules, point it out.

## When You're Unsure

**Ask for the testing approach:** If you're unsure how to test a component, ask for the testing strategy before implementing.

**Suggest alternatives:** If you see multiple ways to implement something, present them for decision.

**Check before reading:** Always confirm file paths with Claude before reading to avoid token waste.

**Stop for verification:** After making changes, suggest verification steps before moving to the next task.