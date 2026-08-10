# Overseer Framework

**RESPONSE FORMAT: Always start your responses with '[🏗️ OVERSEER CREATION AGENT]' on the first line, then continue with your message.**

**INITIALIZATION INSTRUCTIONS**: When this agent is loaded, you must:
1. Read all documents listed in the Document Index below
2. Ensure you understand the complete workflow and guidelines before proceeding
3. Update the Document Index if new documents are added during development

A framework-agnostic AI agent governance system for controlling tool usage, enforcing policies, and managing compliance across different CLI environments.

## Critical Rules

- **Layer Independence**: Each layer must be independent with minimal coupling to other Overseer files
- **Testing-First**: Never implement without a test plan. Test in order: implement → test → verify → fix
- **Modularity**: Follow consistent patterns, use existing libraries, implement base classes with ABC
- **CLI-Agnostic**: No CLI-specific assumptions in core framework
- **State Machine Correctness**: Ensure state transitions are valid and enforceable
- **Logging Standardization**: All implementations must include comprehensive logging to layer-specific JSONL files (e.g., `logs/Adapter-Log-DATE.jsonl`, `logs/Overseer-Log-DATE.jsonl`, `logs/Protocol-Log-DATE.jsonl`). This applies even to schema-only definitions - logging initialization, usage, and errors is required regardless of validation scope.
- **Engineering Principles**: Follow guidelines in SOFTWARE_ENGINEERING_PRINCIPLES.md for component modularity, standardization, KISS principle, and testing

## Document Index

- **[WORKFLOW.md](./WORKFLOW.md)**: Complete 26-step governance process with parallel execution and research-first approach
- **[SUBAGENT_ORCHESTRATION.md](./SUBAGENT_ORCHESTRATION.md)**: Detailed subagent coordination guidelines
- **[SOFTWARE_ENGINEERING_PRINCIPLES.md](./SOFTWARE_ENGINEERING_PRINCIPLES.md)**: Software engineering best practices and development guidelines

