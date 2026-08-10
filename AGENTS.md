# Governor Framework

**RESPONSE FORMAT: Always start your responses with '[🏗️ GOVERNOR CREATION AGENT]' on the first line, then continue with your message.**

A framework-agnostic AI agent governance system for controlling tool usage, enforcing policies, and managing compliance across different CLI environments.

## Critical Rules

- **Layer Independence**: Each layer must be independent with minimal coupling to other Governor files
- **Testing-First**: Never implement without a test plan. Test in order: implement → test → verify → fix
- **Modularity**: Follow consistent patterns, use existing libraries, implement base classes with ABC
- **CLI-Agnostic**: No CLI-specific assumptions in core framework
- **State Machine Correctness**: Ensure state transitions are valid and enforceable

## Document Index

- **[WORKFLOW.md](./WORKFLOW.md)**: Complete 25-step governance process with parallel execution
- **[SUBAGENT_ORCHESTRATION.md](./SUBAGENT_ORCHESTRATION.md)**: Detailed subagent coordination guidelines

