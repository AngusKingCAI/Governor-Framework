# Research Report: AI Agent Harness Memory Architectures

**Research Date**: 2026-08-13
**Researcher Agent**: Systematic Investigation
**Subject**: Memory architectures used by top AI developers in their agent harnesses/frameworks

## Executive Summary

**Primary Question**: What are the prevailing memory architectures and implementations used by top AI developers in their agent harnesses/frameworks?

**Key Findings**:
- Top AI frameworks use diverse memory approaches, but converge on similar foundational patterns
- File-based memory is gaining traction for its simplicity and LLM compatibility
- Vector databases remain popular for semantic search but face performance and complexity trade-offs
- Most frameworks treat memory as application-specific rather than universal infrastructure
- Emerging trend toward hierarchical, multi-tier memory architectures

**Confidence Level**: High (based on documentation from major frameworks and comparative studies)

## Research Context

### Research Questions
- **Primary**: What memory architectures are leading AI frameworks using?
- **Secondary**: How do frameworks handle long-term vs. short-term memory? What are common approaches to persistence, retrieval, and management? How do frameworks balance performance, scalability, and effectiveness?

### Scope
- **In scope**: Major AI frameworks (LangChain, CrewAI, AutoGPT, AutoGen), coding harnesses (Claude Code, Cursor), memory infrastructure patterns
- **Out scope**: Project-specific memory implementations, custom agent memory solutions
- **Assumptions**: Focus on harness-level memory, not application-specific memory patterns

## Detailed Findings

### 1. Framework-Specific Memory Architectures

#### LangChain/LangGraph: Low-Level Control Philosophy
**Architecture**: Memory Store with cross-thread persistence
**Key Features**:
- Simple document store with put/get/search primitives
- Flexible namespacing for users, organizations, contexts
- JSON document storage with optional vector search
- Checkpointers for short-term conversation state
- LangMem SDK for long-term memory with automatic extraction

**Memory Types** (CoALA paper classification):
- **Procedural**: LLM weights + agent code (rarely updated dynamically)
- **Semantic**: Facts about the world, used for personalization
- **Episodic**: Sequences of past actions, used for few-shot prompting

**Philosophy**: Application-specific memory with low-level user control

#### CrewAI: Cognitive Memory as Agentic System
**Architecture**: Unified memory system with hierarchical scopes
**Key Features**:
- Single Memory class replacing separate memory types
- LLM-driven content analysis (scope, categories, importance)
- Hierarchical scope tree (filesystem-like organization)
- Adaptive-depth recall with composite scoring
- LanceDB backend for vector storage

**Cognitive Operations**:
- Encode: Analyze content, assign importance, detect contradictions
- Consolidate: Resolve conflicts, organize hierarchically
- Recall: Evaluate confidence, decide depth
- Extract: Retrieve relevant information
- Forget: Purposeful forgetting of outdated information

**Innovation**: Treats memory as an agentic system itself, using CrewAI Flows for memory management

#### AutoGPT: Simplified Vector Memory
**Architecture**: Vector memory with multiple backend support
**Evolution**: Originally supported Pinecone, Weaviate, Milvus, Redis - simplified to JSONFileMemory due to maintenance overhead
**Current State**:
- JSONFileMemory as default (local file-based)
- Focus on performance during single runs
- Limited cross-session persistence
- KNN search for relevant memory retrieval

**Trade-off**: Prioritized working memory functionality over long-term persistence

#### Microsoft AutoGen: Protocol-Based Extensibility
**Architecture**: Memory protocol with pluggable implementations
**Key Features**:
- Abstract Memory protocol (query, update_context, add, clear, close)
- ListMemory as simple chronological implementation
- Support for custom vector database implementations
- Event-driven architecture for memory updates
- Layered architecture (Core API vs AgentChat API)

**Pattern**: Framework provides protocol, users implement storage mechanism

### 2. Coding Harness Memory Approaches

#### Claude Code: File-Based Hierarchical Memory
**Architecture**: 4-level CLAUDE.md hierarchy with 5-layer compaction
**Structure**:
- Managed (`/etc/`) → User (`~/.claude/`) → Project (`CLAUDE.md`) → Local (`CLAUDE.local.md`)
- File-based memory (no vector DB)
- Fully inspectable, editable, version-controllable

**Compaction Strategy**:
- Budget reduction → Snip → Microcompact → Context Collapse → Auto-compact
- Graduated lazy-degradation to manage token limits
- Auto-compacting and hierarchical summarization

**Advantages**: Simplicity, LLM compatibility, transparency

#### Cursor: Codebase-Centric Memory
**Architecture**: Raw context stuffing with aggressive retrieval
**Approach**:
- Prioritizes codebase as primary memory
- Local vector DB with embeddings
- Parallel file listing for context gathering
- Aggressive retrieval vs. selective summarization

**Philosophy**: "Your codebase doesn't lie" - source code as canonical memory

### 3. Infrastructure Patterns and Best Practices

#### Two-Layer Memory Pattern
**Pattern**: Separate persistent memory (canonical) from derived context
**Key Principle**: Derived context points back to canonical memory, never vice versa
**Implementation**:
- **Persistent Memory**: Long-term canonical record (facts, decisions, policies)
- **Derived Context**: Shaped for specific access patterns (embeddings, summaries, pre-joined views)
- **Authority Rule**: When they disagree, persistent memory wins

#### Three-Tier Memory Architecture
**Pattern**: Working memory → Agent memory → Shared memory
**Tiers**:
- **Tier 1**: Working memory (per-task, ephemeral, auto-pruned)
- **Tier 2**: Agent memory (per-agent, summarized periodically, versioned)
- **Tier 3**: Shared memory (cross-agent, write-gated, read-optimized)

#### OS-Inspired Virtual Context (MemGPT)
**Architecture**: Treat LLM context window like OS memory management
**Key Innovation**:
- **Main Context**: LLM prompt tokens (system instructions, working context, FIFO queue)
- **External Context**: Vector store + recall database (disk storage)
- **Paging**: LLM manages its own memory via function calls

**Performance**: 93.4% deep memory retrieval accuracy vs 35.3% for recursive summarization

### 4. File-Based vs Vector Database Trade-offs

#### Performance Comparison
**Study Results**:
- **File-based (MEMORY.md)**: 128k tokens, 4m 12s, 18KB footprint
- **Vector retrieval (mem0)**: 213k tokens, 9m 38s, 42MB footprint

**Quality Comparison**:
- **File-based**: 5/5 classic errors caught, 3 relevant historical cases, 0 false positives
- **Vector**: 4/5 errors caught, 8 relevant but redundant cases, 1 false positive

#### File System Advantages
**LLM Compatibility**: Models already know how to use filesystems
**Simplicity**: No embedding pipeline, direct text storage
**Transparency**: Fully inspectable and editable
**Performance**: Faster for small-to-medium knowledge bases

#### Database Advantages
**Semantic Retrieval**: Vector search finds content by meaning, not keywords
**Scalability**: Indexing, clustering, caching for large knowledge bases
**Concurrency**: Multi-user support with proper locking
**Security**: Fine-grained RBAC and auditing

**Transition Point**: Filesystems win until you need correctness under concurrency, semantic retrieval, or structured guarantees

### 5. Cross-Framework Memory Infrastructure

#### Current Limitation
**Problem**: Memory is scoped to individual frameworks
- LangGraph memory inaccessible to Claude Code/Cursor
- No cross-framework memory standard
- Each framework treats memory as framework feature, not infrastructure

#### Emerging Solutions
**MCP Server Approach**: Model Context Protocol for cross-framework memory access
**Universal Memory API**: Standardized memory interface across frameworks
**Memory as Infrastructure**: Separate memory layer from framework logic

## Analysis and Synthesis

### Consistent Patterns Across Frameworks

1. **Multi-Tier Architecture**: All frameworks separate short-term (session) from long-term (persistent) memory
2. **Application-Specific Design**: Memory requirements vary significantly by use case
3. **Hierarchical Organization**: Memory organized by scope (user, project, agent, task)
4. **Hybrid Retrieval**: Combining semantic search with structural/keyword filtering
5. **Background Processing**: Memory updates often separated from hot path for performance

### Key Architectural Decisions

#### Memory Update Strategies
**Hot Path**: Agent explicitly decides to remember before responding (ChatGPT approach)
**Background Process**: Separate process updates memory during/after conversation (LangGraph approach)
**User Feedback**: Memory updates based on user interaction feedback (episodic memory)

#### Persistence Strategies
**File-Based**: Simple, LLM-compatible, transparent (Claude Code)
**Vector Database**: Semantic search, scalable, complex (CrewAI, LangGraph)
**Hybrid**: File system interface with database substrate (Oracle AI Database)

#### Scope Management
**Hierarchical Scopes**: Filesystem-like organization (CrewAI)
**Namespaced Storage**: Custom namespaces for different contexts (LangGraph)
**User/Project Separation**: Cross-session vs. per-session boundaries (AutoGen)

### Performance vs. Complexity Trade-offs

**Simplicity End**: File-based memory (Claude Code)
- Pros: Fast, simple, transparent, LLM-compatible
- Cons: Limited semantic retrieval, scalability issues

**Complexity End**: Vector databases with cognitive processing (CrewAI)
- Pros: Advanced semantic retrieval, conflict resolution, hierarchical organization
- Cons: Complex, slower, requires infrastructure

**Middle Ground**: Hybrid approaches (LangGraph, AutoGen)
- Pros: Balance of simplicity and functionality
- Cons: Still requires infrastructure management

## Knowledge Gaps

### Missing Information
- **Long-term Performance**: Limited data on memory system performance over months/years
- **Cross-Framework Standards**: No clear winner for universal memory infrastructure
- **Enterprise Requirements**: Limited information on enterprise-grade memory requirements (security, compliance, governance)
- **Cost Analysis**: Insufficient data on total cost of ownership for different approaches

### Quality Limitations
- **Benchmarks**: Limited standardized benchmarks for memory system comparison
- **Real-World Data**: Most comparisons are synthetic or small-scale
- **Framework Evolution**: Rapid framework changes make long-term analysis difficult

## Conclusions and Recommendations

### Evidence-Based Conclusions

1. **No Universal Solution**: Memory requirements are inherently application-specific; no one-size-fits-all approach exists
2. **File-Based Resurgence**: File-based memory is surprisingly effective for many use cases, challenging the assumption that vector databases are always superior
3. **Framework Lock-in**: Current memory implementations are framework-specific, creating silos that limit interoperability
4. **Cognitive Memory Trend**: Moving toward memory systems that actively process and organize information rather than passive storage
5. **Two-Layer Pattern**: Separation of canonical memory from derived context is emerging as best practice

### Recommendations for Harness Design

**For Simple Use Cases**:
- Start with file-based memory (MEMORY.md pattern)
- Add hierarchical organization as needs grow
- Consider vector database only when semantic retrieval becomes critical

**For Complex Use Cases**:
- Implement two-layer pattern (canonical + derived)
- Use hierarchical scopes for organization
- Add cognitive processing for conflict resolution and importance ranking

**For Production Systems**:
- Plan for concurrency, security, and compliance requirements
- Implement proper audit trails and provenance tracking
- Design for cross-framework interoperability where possible

### Limitations and Caveats

- **Rapid Evolution**: AI memory field is evolving quickly; recommendations may change
- **Framework Bias**: Research focused on major frameworks; may miss innovative approaches
- **Performance Context**: Benchmarks may not reflect real-world usage patterns
- **Application Specificity**: Optimal memory design depends heavily on specific use case

### Areas for Further Investigation

- **Standardization Efforts**: Monitor development of cross-framework memory standards
- **Enterprise Requirements**: Research security, compliance, and governance requirements
- **Performance at Scale**: Long-term performance data for large-scale memory systems
- **Cognitive Memory**: Deep dive into cognitive memory architectures and their effectiveness

## References

- LangChain Memory Blog: https://www.langchain.com/blog/memory-for-agents
- LangGraph Long-Term Memory: https://www.langchain.com/blog/launching-long-term-memory-support-in-langgraph
- CrewAI Memory Documentation: https://docs.crewai.com/en/concepts/memory
- CrewAI Cognitive Memory: https://blog.crewai.com/how-we-built-cognitive-memory-for-agentic-systems/
- AutoGPT Memory Revamp: https://github.com/Significant-Gravitas/AutoGPT/pull/4208
- AutoGen Memory Protocol: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html
- MemGPT Paper: https://par.nsf.gov/servlets/purl/10524107
- File vs Vector Comparison: https://chenguangliang.com/en/posts/ai-agent-memory-file-vs-vector/
- Two-Layer Pattern: https://blogs.oracle.com/developers/persistent-memory-and-derived-context-a-two-layer-pattern-for-agents
- Claude Code Architecture: https://github.com/VILA-Lab/Dive-into-Claude-Code
- Harness Comparison: https://mem0.ai/blog/harness-comparison-how-claude-code-cursor-devin-and-antigravity-each-handle-memory
- Cross-Framework Analysis: https://memnexus.ai/blog/2026-04-07-agentic-framework-memory-comparison