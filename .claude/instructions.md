# Governor Framework - Claude Instructions

## Token Efficiency Rules

**Always ask before reading files:** Before reading any file, confirm the exact path with Claude to avoid wasted reads.

**Be specific and concise:** Use short, direct prompts. Long prompts waste tokens without adding value.

**Read before write:** Always check if a file exists before attempting to write it.

**Use file lists:** When working with multiple files, list them in one prompt rather than asking individually.

**Batch operations:** Group related operations into single prompts to reduce overhead.

## Project Context

**Architecture:** Governor Framework is a layered AI agent governance system:
- Layer 1: `governor.py` (entry point, minimal logic)
- Layer 2: `hook_handlers/` (specific hook implementations)
- Layer 3: `state_machine.py` (state management, self-contained)
- Layer 4: `engine.py` (rule evaluation)
- Layer 5: `actions/` (governance actions)
- Layer 6: `protocol.py` (response formats)
- Layer 7: `audit_log.py` (logging)

**Key Principle:** Each layer should be independent with minimal coupling. No layer should import from other Governor files except as specified.

## File Structure

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
├── cli/ (CLI detection - FUTURE)
├── rules/ (YAML rule files)
├── templates/ (rule templates)
├── state/ (runtime state storage)
└── logs/ (execution logs)
```

## Current Issues to Address

**State Machine Concerns:** The compliance state machine may not be working as intended. Focus your analysis on:
- Phase transition logic (INIT, EXECUTE, RESEARCH, PLAN, VALIDATE, COMMIT)
- Compliance state transitions (testing_in_progress, testing_complete, blocked, ready_to_proceed)
- State transition validation and enforcement
- Whether the state machine is actually preventing unauthorized actions

**Layer Boundaries:** Check if layers are truly independent or if there are hidden dependencies violating the stated architecture.

## Build and Test Commands

**No build process:** This is a Python framework with no compilation step.

**Testing approach:** Before making changes, identify what should be tested first rather than implementing without verification.

**File verification:** Always confirm you're looking at the correct file by checking the path with Claude before reading.

## Working Style

**Plan before implement:** Ask Claude to describe its approach before making changes.

**Focus on one layer at a time:** Don't try to fix multiple layers simultaneously.

**Small changes:** Make incremental changes rather than large refactors.

**Test each change:** After each modification, consider how to verify it works correctly.

## When You're Unsure

**Ask for clarification:** If instructions are ambiguous, ask rather than assuming.

**Suggest alternatives:** If you see multiple approaches, present them for decision.

**Flag token-heavy operations:** If an action would require reading many files, ask if there's a more efficient approach.