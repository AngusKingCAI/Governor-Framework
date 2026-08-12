# Overseer Framework

**RESPONSE FORMAT: Always start your responses with '[🏗️ OVERSEER CREATION AGENT]' on the first line, then continue with your message.**

**INITIALIZATION INSTRUCTIONS**: When this agent is loaded, you must:
1. **SELECT WORKFLOW**: Use ask_user_question to ask which workflow to load:
   - **Implementation Workflow**: For new features, components, or architectural changes (Workflows/IMPLEMENTATION_WORKFLOW.md)
   - **Fix Workflow**: For addressing external review findings, security issues, or quality improvements (Workflows/FIX_WORKFLOW.md)
2. Read the selected workflow document from Workflows/ directory
3. Read all documents listed in the Document Index below
4. Ensure you understand the complete workflow and guidelines before proceeding
5. Update the Document Index if new documents are added during development

A framework-agnostic AI agent governance system for controlling tool usage, enforcing policies, and managing compliance across different CLI environments.

## Critical Rules

- **Layer Independence**: Each layer must be independent with minimal coupling to other Overseer files (ARCHITECTURE.md Principle 2)
- **Testing-First**: Never implement without a test plan. Test in order: implement → test → verify → fix (SOFTWARE_ENGINEERING_PRINCIPLES.md)
- **Modularity**: Follow consistent patterns, use existing libraries, implement base classes with ABC (ARCHITECTURE.md Principle 2)
- **True Agnosticism**: Core framework must make ZERO assumptions about adapters or environment (ARCHITECTURE.md Principle 1)
  - No hardcoded event types or registries (must be dynamically registered by adapters)
  - No hardcoded naming conventions (must be configurable)
  - No CLI-specific assumptions in code or documentation
  - Adapters should be the ONLY flexible component
  - Protocol/Overseer layers must be completely environment-independent
  - Core system must adapt to whatever adapters provide
- **State Machine Correctness**: Ensure state transitions are valid and enforceable
- **Logging Standardization**: All implementations must include comprehensive logging to layer-specific JSONL files (e.g., `logs/Adapter-Log-DATE.jsonl`, `logs/Overseer-Log-DATE.jsonl`, `logs/Protocol-Log-DATE.jsonl`). This applies even to schema-only definitions - logging initialization, usage, and errors is required regardless of validation scope (ARCHITECTURE.md Principle 9)
- **Security-First Development**: Follow security principles from ARCHITECTURE.md Principles 23-27:
  - Input Validation and Prompt Injection Defense (Principle 23)
  - Defense in Depth with Layered Security (Principle 24)
  - Least Privilege and Zero Trust Enforcement (Principle 25)
  - Reversibility-Weighted Risk Enforcement (Principle 26)
  - Subagent Isolation and Delegation Boundaries (Principle 27)
- **Engineering Principles**: Follow guidelines in SOFTWARE_ENGINEERING_PRINCIPLES.md for component modularity, standardization, KISS principle, and testing

## Document Index

### Implementation Documents
- **[ARCHITECTURE.md](./Implimentation Docs/ARCHITECTURE.md)**: 27 consolidated architectural principles for Overseer core governance system
- **[IMPLEMENTATION.md](./Implimentation Docs/IMPLEMENTATION.md)**: Coding conventions, patterns, and implementation guidance with zero external dependencies
- **[ORGANIZATIONAL_GUIDE.md](./Implimentation Docs/ORGANIZATIONAL_GUIDE.md)**: ISO 42001 alignment and enterprise deployment guidance
- **[SOFTWARE_ENGINEERING_PRINCIPLES.md](./Implimentation Docs/SOFTWARE_ENGINEERING_PRINCIPLES.md)**: Software engineering best practices and development guidelines
- **[SUBAGENT_ORCHESTRATION.md](./Implimentation Docs/SUBAGENT_ORCHESTRATION.md)**: Detailed subagent coordination guidelines
- **[EXTERNAL_REVIEW_PROMPT.md](./Implimentation Docs/EXTERNAL_REVIEW_PROMPT.md)**: External AI review prompt with websearch verification requirements

### Workflows
- **[IMPLEMENTATION_WORKFLOW.md](./Workflows/IMPLEMENTATION_WORKFLOW.md)**: Development workflow for new features and components with TDD enforcement
- **[FIX_WORKFLOW.md](./Workflows/FIX_WORKFLOW.md)**: Systematic workflow for addressing external review findings, security issues, and quality improvements
- **[RESEARCH_WORKFLOW.md](./Workflows/RESEARCH_WORKFLOW.md)**: Documentation refinement workflow through iterative hyper-specific research to make documentation implementation-ready


