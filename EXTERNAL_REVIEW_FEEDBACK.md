# External Review Feedback for PRINCIPLES.md

**Date**: 2026-08-11  
**Purpose**: Systematic review of 34 architectural principles for quality, contradictions, and gaps

---

## Quality Issues

**[Document structure / Principle 1]**: The retrieved document is internally inconsistent: content for Principle 1.5 appears immediately after Principle 11.2, and Principle 2 begins after Principle 1 success criteria. Verify the source ordering before relying on cross-principle references.

**[Principle 9]**: "Extensive, extremely verbose" logging is subjective and not testable. Replace with defined event categories, mandatory fields, retention, redaction, access control, integrity, and an explicit rule that sensitive tool inputs/outputs are minimized or masked. NIST AI RMF treats security, privacy, transparency, and accountability as co-equal governance concerns; exhaustive logs can conflict with privacy and security if unbounded.

**[Principle 9.1]**: Requiring every file to own a logging function and log file is an implementation prescription, not an architectural principle. It can fragment traceability across an action. State the architectural outcome instead: one correlation identifier and an auditable, protected end-to-end decision trail.

**[Principle 11]**: "Follow SOLID" is a broad coding guideline rather than an Overseer architecture principle. It lacks a governance-specific boundary, decision rule, and measurable success criterion. Its sub-principles also mix desired outcomes, implementation choices, examples, and benefits inconsistently.

**[Principle 11.1]**: "One primary responsibility" is ambiguous without defining responsibility at the framework boundary. A reviewer cannot reliably determine whether a class violates it.

**[Principle 11.2]**: "Use interfaces and abstractions" is too generic and risks abstraction for its own sake. Make the extension points explicit: adapter contract, policy-evaluation contract, event schema/versioning contract, and enforcement-result contract.

**[Principle 25]**: "Binary" conflicts with its own three stated outcomes: allow, deny, and modify. "Modify" also needs a defined semantics: whether it is a terminal enforcement result, a required transformation followed by re-evaluation, and which component is authorized to perform it.

**[Principle 25.1]**: A rule such as "Block file deletion" is not sufficient for testability. Define policy inputs, precedence/conflict resolution, default behavior on missing context, versioning, and expected evidence recorded with each verdict.

**[Principle 1.5]**: "ANY environment," "zero" tool-specific references, and "ZERO framework code changes" are absolute claims without scope. Define supported portability boundaries and allow documented capability negotiation; otherwise normal platform-specific security controls or transport behavior appear to violate the principle.

**[Principle 2]**: Implementation masquerading as principle. Mandating that hooks point to `overseer.py` is a specific file dependency, not an architectural guideline. It lacks rationale for why centralizing on a filename is superior to an interface contract, and it directly undermines Principle 1's claim of "True Agnosticism."

**[Principle 15]**: "Silent failure pattern" is dangerously vague for a governance system. The principle does not clarify whether "silent" means fail-open (allow traffic), fail-closed (block traffic), or log-only. A governance hook that fails silently without a defined, safe default creates an unquantifiable security gap.

**[Principle 18]**: Performance targets are requirements, not principles. Specifying `<0.1ms` p50 allow and `<0.5ms` p99 deny are brittle SLAs. Enterprise architecture principles should be "stable yet flexible" statements that guide design decisions across technology generations; hardcoded millisecond thresholds belong in a Service Level Objective document, not an architectural principles list.

**[Principle 1 & Principle 4]**: Redundant and indistinct. "True Agnosticism" and "Zero-Assumption Framework" both assert "zero assumptions" without a clear boundary between them. Principles must be mutually exclusive in scope to be actionable; these two collapse into a single concept and confuse decision-making.

**[Principle 4.2]**: "Metadata-driven processing" is vague. What metadata schema? How is conformance tested? "Checks event metadata" without specifying contract makes it untestable.

**[Principle 6]**: "Open string identifiers" is ambiguous. Are these URIs, UUIDs, free-text? Conflicts with Principle 9's need for structured logging that requires identifiable fields.

**[Principle 10]**: "Small focused functions (<50 lines)" is an arbitrary metric without rationale. Web search confirms line-count limits are widely debated; prefer "single responsibility" framing.

**[Principle 14.x Meta Rule Governance]**: Important idea, weak boundary. Does not define who can change meta-rules, bootstrapping order, or protection against meta-rule compromise (governance of governance).

**[Principle 16]**: Overly implementation-specific ("Python execution files", directory paths). Principles should state organizational intent (separate system vs user actions); file layout belongs in an implementation standard.

**[Principle 2.3]**: Actionable direction (centralize in `overseer.py`) but weak rationale for why centralization beats a thinner orchestrator + policy engine. Risks a god-object unless bounded by Principle 11/12.

**[Principle 3]**: Naming drift in retrieved text ("Config-Driven" vs "Config-Based"). Definition is clear; testability is only partial—does not define precedence when config, adapter claims, and meta-rules disagree.

**[Principle 6.1]**: "Any string is valid" is clear but under-specified for safety. Open identifiers without namespace/authority rules hurt auditability and collision resistance.

**[Principle 33]**: Title "Stateless Enforcement" contradicts its own definition ("given rule state"). Rename to "Minimize Temporal Coupling; Externalize State Explicitly."

**[Principles 2, 13, 16]**: Reference specific filenames (`overseer.py`), file formats (YAML + Python), and directory layouts. These are technology choices, not principles — inconsistent abstraction level vs. Principles 1 and 25–34. TOGAF's principle quality criteria require principles to be robust and stable across implementations.

**[Principle 1 success criteria]**: "Documentation contains zero tool-specific references" is unachievable and self-contradicting — sub-principles 1.2 and 3.1 give tool-specific examples (Devin-Adapter.py).

**[Principle 8]**: "Extreme modularization" is vague and "each file completely independent" is untestable; heavily overlaps Principle 12 (Component Modularity). Merge or delineate scope.

**[Numbering — Principles 18–20]**: Sub-principles are numbered 14.x, 15.x, 16.x — offset by four from their parents. Principle 20's "16.1/16.2" collides with Principle 16's actual "16.1/16.2" (two different sub-principles share ID 16.1). Clear evidence of renumbering drift.

**[Numbering/Format]**: Principle 11 jumps 11.2 → 11.5 in visible content (verify 11.3/11.4 exist); Principles 5, 10, 14, 15, 17, 21–23, 29–30 could not be surfaced by retrieval — verify they exist and are correctly numbered given the claimed count of 34. Success Criteria sections are present on some principles (1, 7, 11, 26, 27, 32, 33) and absent on others — standardize.

**[Principles 19/15.2 and 24.2]**: Both are named "Hook Isolation" with different meanings (failure isolation vs. data isolation). Rename one.

---

## Contradictions

**[Principle 9] vs [Principle 1.5]**: Per-file, layer-specific logging implies environment- and file-layout-specific operational behavior, while 1.5 requires environment-independent core layers and no tool-specific references. This is a real architectural tension: centralize portable audit-event semantics in the core, then let deployment-specific sinks be adapters. NIST AI RMF supports governance across lifecycle contexts, while ISO/IEC 42001 emphasizes an AI management system that is maintained and continually improved rather than fixed to one deployment pattern.

**[Principle 9] vs [Principle 25]**: "Track everything" can capture sensitive prompts, secrets, or personal data, whereas deterministic, auditable policy enforcement needs only sufficient decision evidence. This is an actual conflict unless Principle 9 adds data minimization, redaction, and role-based access. NIST identifies privacy-enhanced and secure/resilient AI as trustworthy characteristics alongside accountability and transparency.

**[Principle 11.2] vs [Principle 1.5]**: Extension "through interfaces and abstractions" is compatible with portability, but "adding a new adapter requires zero framework changes" is only valid if the adapter contract already expresses all required capabilities. Novel tool semantics may require contract evolution. Treat this as an explicit, acceptable trade-off by adding versioned contracts and capability negotiation.

**[Principle 25] vs [Principle 1.5]**: Deterministic verdicts require stable policy inputs and canonical event semantics; unconstrained adapters/environments can supply incomplete or inconsistent context. This is a genuine tension, not a contradiction, if the framework defines a canonical authorization request and fails closed when required context is absent.

**[Principle 1.4 (Dynamic Adaptation)] vs [Principle 3 (Config-Driven Adapter Selection)]: TOGAF emphasizes that principles must be clear and stable enough to guide decisions; conflicting principles undermine architecture governance. You cannot simultaneously discover adapter capabilities at runtime (1.4) and declare them upfront in config (3.1). Choose one: either config-driven (static, validated upfront) or dynamic discovery (runtime, flexible but harder to reason about). Current design should be config-driven; remove 1.4 or reframe it as "Framework accepts runtime registration only after config declares adapter."

**[Principle 6 (Fail-Closed)] vs [Principle 28 (Incremental Capability Adoption)]: The autonomy-versus-robustness trade-off shows that tighter governance improves safety but can slow execution or block useful behavior. If teams adopt Overseer incrementally (e.g., only hooking PreToolUse, not PostToolUse), then unmonitored hooks default to pass-through. This is fail-open for unmapped hooks, violating Principle 6. Success Criteria for 28 must explicitly address how fail-closed is maintained during partial adoption.

**[Principle 18 (Atomic Operations)] vs [Principle 33 (Stateless Enforcement)]**: If hooks are stateless (33.1: "independently decidable"), how can they participate in atomic multi-hook transactions (18.1)? Atomic operations require coordinated state across invocations; stateless enforcement cannot coordinate. Success Criteria conflict: 18 requires "atomic guarantees," 33 requires "no temporal state dependencies." Clarify scope: are individual hook decisions stateless while aggregate rule sets are transactional, or is this a real conflict?

**[Principle 25 (Supply Chain Integrity)] vs [Principle 1.1 (Zero Hardcoded Assumptions)]**: Checking adapter signatures/provenance requires knowing which adapters are "approved." This means the framework does have hardcoded assumptions about adapter identity/trust. Either adapt 1.1 to allow identity-based assumptions, or move supply-chain checks to deployment layer (outside Overseer core).

**[Principle 9] vs [Principle 33 - No Silent Failures]**: Comprehensive Logging prescribes silent failure as fallback (try file → stderr → silent), while Principle 33 mandates no silent failures. Direct conflict. — Web search (Claude Code hooks, endorlabs hook governance) confirms fail-closed is the standard for governance systems; silent failure undermines audit integrity.

**[Principle 4 - Zero-Assumption Framework] vs [Principle 2 - Overseer-Centric]**: Zero-Assumption demands framework make no assumptions, but Overseer-Centric mandates `overseer.py` as THE integration point — a hard architectural assumption. Tension: agnosticism vs. mandated integration point. Acceptable trade-off only if `overseer.py` is itself replaceable (not stated).

**[Principle 8 - Extreme Modularization] vs [Principle 7 - Layer Independence]**: Extreme modularization (file independence, minimal imports) may conflict with layer independence's stable interface contracts. If every file is self-contained, shared interface definitions become duplicated, violating DRY and creating drift risk. — TOGAF warns against over-modularization fragmenting architectural coherence.

**[Principle 11.2 - Open/Closed (new adapters no core changes)] vs [Principle 3 - Config-Driven Adapter Selection]**: Config-driven selection implies framework reads adapter config at runtime (behavior modification), which can blur OCP compliance if config effectively changes core behavior. Clarify boundary.

**[Principle 13 (Determinism) vs [Principle 1 (True Agnosticism)]**: Principle 13 states "Declarative policy engines that evaluate structured authorization requests against explicit rules are verifiable and deterministic." But Principle 1 says framework makes "ZERO functional assumptions about adapters." If you assume all governance is declarative + deterministic, you've hardcoded a governance model, violating true agnosticism. Enterprise governance increasingly requires probabilistic/risk-weighted decisions (e.g., "high-risk actions require escalation" not hard deny), which conflicts with strict determinism. Clarify: does Overseer support non-deterministic policies, or is determinism an absolute requirement?

**[Principle 4 vs [Principle 7]**: Principle 4 says "Policy Management: Users create rules as YAML files." Principle 7 says "Policy Language: Support multiple policy languages (Cedar, OPA, etc.)." If users write YAML rules but framework supports arbitrary languages, how does rule discovery work? Do all rules get transpiled to canonical form? When? Success Criteria needed: "Rules are loaded in [specific format], optionally compiled to [canonical engine], and validated against adapter hooks before activation."

**[Principle 15] vs [Principle 31]**: Mutually exclusive failure modes. Principle 15 prescribes a "silent failure pattern," while Principle 31 states "No Silent Failures" and demands "immediate, contextual denial notifications" with fail-fast behavior. A system cannot simultaneously suppress failure notifications and emit immediate denial notifications. — Enterprise architecture best practices require a single, explicit failure mode for governance controls; contradictory failure specifications guarantee inconsistent runtime behavior.

**[Principle 20] vs [Principle 26]**: Opposing default security postures. Principle 20 establishes an "advisory (log-only) default mode," meaning traffic is allowed by default. Principle 26 demands "In-Path Enforcement (Fail-Closed)" with "fail-closed defaults." These are architecturally incompatible defaults: one is permissive, the other restrictive. — Security architecture standards consistently mandate fail-closed defaults for enforcement systems; advisory mode should be an operational configuration, not a top-level architectural principle, because it fundamentally disables the enforcement mechanism by default.

**[Principle 33] vs [Principle 30]**: Stateless enforcement cannot track chains. Principle 33 requires "independently decidable hooks without cross-hook or temporal dependencies," while Principle 30 requires "complete chain-of-custody tracking" and "role propagation" across delegation chains. Tracking a chain of custody inherently requires correlating state and identity across multiple hook invocations. — Chain-of-custody is a stateful concept in information systems; enforcing strict statelessness prevents the correlation required to satisfy accountability across a delegation sequence.

**[Principle 32] vs [Principle 9]**: Context minimism conflicts with observability. Principle 32 mandates "Minimal Context Passing" with "no ambient state," while Principle 9 requires "Comprehensive Logging" with structured JSONL containing trace metadata. Meaningful comprehensive logging requires contextual data (identity, resource state, policy context), which minimal context passing explicitly restricts. — This tension is only resolvable with an explicit scoping protocol defining exactly what context is essential for audit; the document provides no such mediation.

**[Principle 14 System self-governance] vs [Principle 26 Fail-closed]**: If meta-rule/action validation fails, does the system block all agent actions or only reject rule changes? Unspecified self-host governance can deadlock operations. — Control-plane vs data-plane separation is a standard resolution.

**[Principle 6 Open string identifiers] vs [Principle 25 Determinism + verifiable policy]**: Unbounded open strings increase ambiguity in policy authoring/audit unless canonicalization/namespaces exist. — Authorization systems (OPA/Cedar-style) favor typed/structured attributes for deterministic evaluation.

**[Principle 25 Binary/deterministic verdicts] vs [Product behavior: bypass menus]**: Bypass/override paths can reintroduce non-determinism or soft-fail behavior if not governed as explicit, audited policy transitions. — Fail-closed security models treat overrides as privileged, logged control-plane actions, not ad-hoc UX escapes.

**[Principle 26 In-path enforcement] vs [Principle 28 Hooks for observability/cost/profiling]**: Same interception path for enforcement and telemetry can create performance/availability pressure and mixed failure domains (e.g., log failure blocking actions, or dual-use complexity). — SRE/security practice often isolates enforce path from best-effort observability side-effects.

**[Principle 1 & 4 Zero-Assumption] vs [Principle 16 Python/Actions layout]**: Core "no assumptions" conflicts with Python-centric action packaging. — Plugin systems usually standardize a runtime contract, not a single language/directory, unless the product deliberately scopes to Python.

**[Principle 19] vs [Principle 26]**: P19 mandates fail-open on hook failure ("default to allow"); P26.2 mandates fail-closed by default. Both claim to define default failure behavior — a genuine conflict, not a trade-off, since neither declares precedence. Confirmed: security-canon guidance (NIST SP 800-123, OWASP error-handling guidance, Saltzer & Schroeder "fail-safe defaults") recommends fail-closed for security controls; fail-open should be an explicit opt-in.

**[Principle 19 / 15.1] vs [Principle 31 / 31.3]**: 15.1 requires a "silent failure pattern"; 31.3 explicitly requires "No silent failures." Direct contradiction.

**[Principle 20] vs [Principle 26]**: "Advisory by default (log only)" vs. mandatory in-path pre-execution blocking. Also sits in tension with zero-trust default-deny (NIST SP 800-207). Confirmed: policy engines resolve this by separating enforcement mode from failure mode (OPA monitor vs. enforce; Istio permissive vs. strict; WAF detection vs. prevention). The document needs that explicit separation and a stated precedence.

**[Principle 9] vs [Principle 18]**: Comprehensive synchronous verbose logging cannot fit a sub-0.1ms hot path. Confirmed: latency-sensitive systems move logging off the critical path (async/buffered/sampled) — the document must specify this or one principle always violates the other.

**[Principle 13] vs [Principle 27]**: P13 hardcodes YAML rules + Python execution files; P27 demands engine-agnostic declarative policy (Cedar, OPA pluggable) and lists "policy logic independent of implementation" as success criteria. Confirmed: the policy-as-code ecosystem (OPA/Rego, Cedar, OpenFGA) treats policy language as pluggable — P13 violates P27.

**[Principle 33] vs [Principle 28]**: Stateless enforcement vs. cost tracking/compliance auditing via hooks — both inherently require accumulated state (as do rate limits and budgets). Confirmed: admission-control designs (Kubernetes admission webhooks, Envoy filters) externalize or explicitly scope state rather than banning it.

**[Principles 1/4] vs [Principle 34]**: "Zero assumptions / zero hardcoded event types" vs. a canonical hook payload model (action type, agent identity, resource, access level, audit context). Resolvable but unreconciled — Confirmed: this is the canonical-model pattern from enterprise integration (Hohpe & Woolf); adapters map native formats into a canonical model. State this explicitly so the principles stop appearing to conflict.

**[Principle 1 success criteria] vs [Principle 3.2]**: "Overseer layer contains zero adapter-specific logic" vs. "overseer maps rules accordingly" per adapter. If mapping is not fully metadata-driven from adapter-declared capabilities, the overseer must know adapter hook names — violating P1. Clarify that mapping is data-driven.

---

## Missing Principles

**[Policy lifecycle and change control]**: Policies should be versioned, reviewed, approved, tested, rolled back, and linked to every enforcement decision. This is necessary for reproducibility and accountability; deterministic evaluation is insufficient if the applicable policy cannot be identified. ISO/IEC 42001 calls for an AI management system that is established, maintained, and continually improved, and NIST AI RMF's GOVERN function applies across the risk-management lifecycle.

**[Fail-safe enforcement and availability]**: Define behavior when the hook, policy engine, adapter, audit store, or context lookup fails: fail closed for high-risk actions, with explicit, approved fail-open exceptions and alerting. Hook-based governance is otherwise bypassable during outages or partial failures. NIST AI RMF includes safety, security/resilience, and risk management as core trustworthy-AI concerns.

**[Canonical authorization context]**: Every intercepted action should be evaluated from a normalized, versioned request containing actor/agent identity, delegated authority, tenant, tool/action, target, parameters classification, environment, purpose, and risk context. This is the prerequisite for portable deterministic policy evaluation across adapters.

**[Identity, delegation, and least privilege]**: Govern not only the tool call but who the agent acts for, what authority was delegated, its scope, expiry, and revocation. This prevents a correctly intercepted call from exercising excessive or stale authority. NIST AI RMF emphasizes accountability and secure/resilient operation.

**[Audit evidence integrity and privacy]**: Audit records should be tamper-evident, access-controlled, retention-bounded, and privacy-minimized. This resolves Principle 9's observability goal without normalizing secret or personal-data collection. ISO/IEC 42001 is designed to support responsible, transparent, and auditable AI management.

**[Policy conflict resolution and exception governance]**: Define precedence among policies, default deny/allow behavior, emergency overrides, approvers, expiry, and post-use review. Without this, deterministic policies can still produce ambiguous outcomes when multiple rules match.

**[Continuous effectiveness measurement]**: Require metrics and periodic testing for coverage, bypass attempts, false blocks, time-to-verdict, policy drift, and incident outcomes. NIST AI RMF explicitly organizes operational risk management around GOVERN, MAP, MEASURE, and MANAGE.

**[Graceful Degradation and Hook Unavailability]**: No major framework has native ACS support yet; many require manual integration with wrappers that add latency and complexity without framework-level guarantees. Overseer lacks guidance on what happens when an adapter doesn't expose an expected hook, or when a hook invocation fails. Do rules fail-safe, re-try, or escalate? How does this interact with Fail-Closed?

**[Policy Versioning and Rollback]**: TOGAF emphasizes that principles should guide organizational decisions and be enduring enough for governance; without versioning, governance changes become unreproducible. Your audit trail (Principle 19) logs what happened but not why rules changed. If a rule update causes cascading blocks, can you roll back? What's the policy version contract?

**[Hook Payload Validation]**: NIST's Govern function requires "mechanisms that facilitate the AI system's auditability" including clear instrumentation of third-party components. You have Principle 34 (Standardized Hook Payloads) but no principle enforcing payload validation. Adapters could send malformed payloads.

**[Performance and Latency Bounds]**: Overseer intercepts every tool use in-path (Principle 2.1), adding latency. ACS specifies sub-millisecond enforcement latencies as a requirement, not a nice-to-have. You have no latency principle. Enterprise teams will demand SLAs.

**[Multi-Adapter Coordination]**: Complex agentic systems require orchestration templates, negotiation boundaries, and coordination checkpoints across agents. Your principles focus on single-adapter governance. What happens when multiple agents using different adapters (Claude Code + Devin) coordinate? Is there a cross-adapter governance boundary?

**[User Override and Emergency Access]**: Your Product Summary says "When Overseer blocks an action, it creates a bypass menu for the user," but this isn't formalized as a principle. Governance maturity models require clear escalation boundaries and human-in-the-loop workflows that adapt as organizational trust increases.

**[Separation of Policy from Mechanism]**: Document covers enforcement mechanisms (hooks, adapters) and policies (YAML rules) but lacks an explicit principle separating policy authoring from enforcement engine. NIST AI RMF and OPA/Cedar best practices mandate this separation.

**[Idempotency / Deterministic Replay]**: Audit principles (22 - Tamper-Evident) exist, but no principle ensures hook execution is deterministic and replayable for forensic reconstruction. Critical for governance systems. — NIST AI RMF emphasizes traceability and reproducibility.

**[Principle of Least Privilege for Hooks]**: Hooks intercept tool usage but no principle constrains hook authority scope. A hook should only access data necessary for its decision. — Microsoft Learn (AI agent governance) and Palo Alto Networks emphasize scoped authority and least privilege as core pillars.

**[Versioning and Backward Compatibility]**: Plugin SDK Pattern (Principle 5) mentions version compatibility but no overarching principle governing API/contract versioning, deprecation policy, or semantic versioning enforcement. TOGAF and enterprise EA standards treat this as foundational.

**[Failure Isolation / Blast Radius Containment]**: Layer Independence (Principle 7) addresses replaceability, not failure containment. No principle ensures a faulty adapter or hook cannot corrupt the audit trail or cascade failures to other layers. — Kore.ai and Galileo AI agent architecture sources identify failure isolation as a governance pillar.

**[Human-in-the-Loop Escalation]**: Product summary mentions "bypass menus" but no architectural principle governs when human review is mandatory vs. optional, or how escalation paths are defined. NIST AI RMF and agentic AI governance standards require explicit human oversight boundaries.

**[Privacy by Design / Data Minimization]**: The document extensively addresses audit trails, tamper-evidence, and digital sovereignty, but never addresses minimizing the sensitive data that hooks intercept, scan, or store. AI governance frameworks (NIST AI RMF, ISO/IEC 42001) universally treat privacy and data minimization as core architectural pillars.

**[Explainability of Governance Decisions]**: While Principle 27 promotes declarative policy and Principle 22 requires audit logs, there is no principle mandating that policy decisions (allow/deny/modify) be explainable or interpretable to operators and end users. NIST AI Risk Management Framework and the EU AI Act both require that automated control decisions be transparent and explainable.

**[Emergency Override / Break-Glass]**: No principle provides for a secure, auditable emergency bypass when normal governance controls would cause critical system failure. Principle 20 allows local overrides, but there is no architectural guideline for structured break-glass access with mandatory post-incident review. — TOGAF and enterprise security architectures require break-glass mechanisms as a first-class governance principle.

**[Configuration and Rule Validation]**: Principles 13–16 define a YAML + Python rule system, yet no principle requires static schema validation, pre-deployment testing, or sandboxed evaluation of rules. Running unvalidated user-provided Python in a sub-millisecond enforcement path introduces both catastrophic performance risk and security escape hatches.

**[Hook Timeout & Bounded Execution]**: Hooks run synchronously in the agent's execution path; a hung hook deadlocks the governed agent. Need max-duration, timeout behavior, and abort semantics. Confirmed: Kubernetes admission webhooks require explicit `timeoutSeconds` and a failure policy; Envoy/git-hook designs make timeout handling a first-class concern. Not covered by P18 (which addresses speed, not hangs).

**[Human Oversight & Escalation]**: No principle covers escalation paths, human approval for high-risk actions, or override workflows. Confirmed: ISO/IEC 42001, NIST AI RMF (GOVERN/MANAGE), and EU AI Act Article 14 all require human oversight measures for high-risk AI decision-making — a core gap for an AI governance framework.

**[Governance Plane Integrity & Least Privilege]**: Nothing protects the governor itself — policy/rule file tampering, malicious adapters, or prompt-injection aimed at the governance layer. Confirmed: OWASP LLM/Agentic guidance lists prompt injection and tool misuse as top risks; Saltzer & Schroeder require least privilege and separation of privilege for the security kernel. The governance plane must be more trusted than what it governs.

**[Tamper-Evident Audit & Retention]**: P9 covers verbosity but not integrity: append-only, signed/hash-chained records, retention, and export for regulatory audit. Confirmed: ISO/IEC 42001 and NIST AI RMF require auditable, integrity-protected records; compliance regimes (e.g., SOC 2) require log integrity controls.

**[Policy Testability & Dry-Run]**: Rules must be unit-testable and deployable in shadow/simulation mode before enforcement. Confirmed: OPA ships policy testing (`opa test`) and dry-run; Cedar provides validation — policy-as-code best practice treats policies as tested code. The document has success criteria for the framework but none for user-authored rules.

**[Contract Versioning & Backward Compatibility]**: P1 promises "ZERO framework code changes" for new adapters, yet nothing governs evolution of adapter contracts, hook payloads, or rule schemas. Confirmed: SemVer/deprecation policies and TOGAF's stability criterion for principles/contracts are standard for extensible platforms.

**[Emergency Controls / Kill Switch]**: No principle for immediate suspension of an agent or tool class, or circuit-breaking a failing adapter. Confirmed: incident-response capabilities (respond/recover) are standard in NIST AI RMF and agent-safety frameworks.

---

## Overall Assessment

**Reviewer 1**: The principles show a useful direction—adapter agnosticism, separation of concerns, observability, and deterministic policy enforcement—but several are aspirational or implementation-specific rather than decision-grade architectural principles. The most urgent work is to repair numbering/order, qualify absolutes, and add lifecycle, failure-mode, identity/delegation, and protected-audit principles.

**Reviewer 2**: The document is comprehensive in scope (34 principles covering agnosticism, governance, audit, and modularity) but suffers from internal contradictions (silent logging vs. no silent failures, agnosticism vs. overseer-centricity) and lacks several governance-essential principles (policy/mechanism separation, least privilege, failure isolation, human-in-the-loop escalation) that web-verified standards (TOGAF, NIST AI RMF, OPA/Cedar) consider foundational.

**Reviewer 3**: The document demonstrates strong domain coverage of runtime mechanics, vendor independence, and cross-CLI standardization, but its architectural coherence is undermined by direct contradictions in failure modes and security defaults, redundant principles that blur decision boundaries, and significant gaps in AI-specific governance such as privacy, explainability, and fairness. Consolidating overlapping principles, resolving the silent-failure contradiction, and replacing implementation-specific mandates with rationale-driven guidelines would materially improve the document's utility as an architectural decision framework.

**Reviewer 4**: The document is ambitious and largely well-structured, but it contains a critical unresolved conflict over default failure behavior (fail-open vs. fail-closed vs. silent-failure vs. fail-fast) plus numbering drift (sub-principles 14.x–16.x under Principles 18–20, duplicate 16.1/16.2 IDs), and it omits human oversight, hook timeouts, and governance-plane integrity. Fix failure-mode precedence, renumber, and add the missing safety principles before this is used as a normative design authority.

---

## Next Steps

1. **Verify numbering consistency** - Fix principle and sub-principle numbering
2. **Resolve failure mode contradictions** - Clarify fail-closed vs fail-open vs silent failure
3. **Add missing principles** - Incorporate governance-essential principles identified
4. **Remove implementation specifics** - Elevate implementation details to implementation standard
5. **Qualify absolute claims** - Replace "zero/any" with scoped, measurable criteria
6. **Standardize format** - Ensure all principles follow consistent structure

---

## Web Search Verification Results

### Fail-Closed vs Fail-Open Security
**CONFIRMED**: Industry standard for governance systems is **fail-closed** for security reasons.
- Microsoft Agent Governance Toolkit: "The policy engine fails closed on all evaluation errors. Any unhandled exception results in an immediate deny"
- OWASP: "Design security mechanism so that a failure will follow the same execution path as disallowing the operation"
- DeepInspect AI Gateway: "Fail-closed is the security mode. Fail-open treats policy as advisory, creating security vulnerabilities"
- ArchMan: "Fail Secure: When failures occur, deny access (fail closed) rather than allow (fail open)"

**Reviewer Assessment**: ACCURATE - The contradiction between Principle 15 (silent failure) and Principle 31 (no silent failures) is real and critical.

### Hook Timeout and Bounded Execution
**CONFIRMED**: Major AI agent systems implement timeout boundaries for hooks.
- Azure SRE Agent Hooks: Default timeout of 30 seconds for command hooks
- Google Gemini API Hooks: Timeout parameter specified (10 seconds in example)
- OpenAI Agents: "Tool guardrail pipeline applies to FunctionTool invocation" with execution control

**Reviewer Assessment**: ACCURATE - Missing hook timeout principle is a significant gap.

### Policy Lifecycle and Versioning
**CONFIRMED**: Policy lifecycle management is a standard requirement for governance systems.
- PolicyCo: "Systematic process of creating, reviewing, approving, distributing, enforcing, and retiring organizational policies"
- V-Comply: "Regulators expect organizations to demonstrate continuous governance, accountability, version control"
- Clarysec: "ISO/IEC 27001:2022 clause 7.5 requires documented information control for policy lifecycle"
- COMPEL Framework: "Seven-stage policy lifecycle: initiation, research, drafting, review, approval, deploy, monitor, retire"

**Reviewer Assessment**: ACCURATE - Missing policy lifecycle principle is a critical gap for enterprise compliance.

### Data Minimization and Privacy by Design
**CONFIRMED**: Data minimization and privacy by design are core requirements for AI governance.
- ICO: "Apply appropriate security risk controls and monitor their effectiveness. Clear audit trails are necessary"
- CNIL AI Checklist: "Ensure processing of personal data is necessary to achieve defined purpose. Check that less intrusive methods cannot achieve same results"
- EDPS EU Guidance: "Data minimisation is one of four general principles alongside fairness, accuracy, security and data subjects' rights"

**Reviewer Assessment**: ACCURATE - Missing data minimization principle contradicts comprehensive logging without privacy controls.

---

## Verified Critical Issues

### 1. Failure Mode Contradiction (CRITICAL)
**Status**: CONFIRMED
**Issue**: Principles 15, 19, 20, 26, 31 have contradictory failure mode specifications
**Industry Standard**: Fail-closed for security systems
**Required Action**: Resolve failure mode precedence and standardize on fail-closed default

### 2. Missing Hook Timeout Principle (HIGH)
**Status**: CONFIRMED  
**Issue**: No principle for hook timeout and bounded execution
**Industry Standard**: All major systems implement timeout boundaries (10-30 seconds)
**Required Action**: Add principle for hook timeout with abort semantics

### 3. Missing Policy Lifecycle Principle (HIGH)
**Status**: CONFIRMED
**Issue**: No principle for policy versioning, change control, lifecycle management
**Industry Standard**: Seven-stage lifecycle is standard for enterprise compliance
**Required Action**: Add comprehensive policy lifecycle principle

### 4. Missing Data Minimization Principle (HIGH)
**Status**: CONFIRMED
**Issue**: Principle 9 requires comprehensive logging without privacy controls
**Industry Standard**: Data minimization and privacy by design are core requirements
**Required Action**: Add data minimization principle or modify Principle 9 with privacy controls

### 5. Implementation Specifics as Principles (MEDIUM)
**Status**: PARTIALLY CONFIRMED
**Issue**: Python paths, file formats, directory layouts elevated to principles
**Industry Standard**: TOGAF requires principles to be technology-agnostic
**Required Action**: Remove implementation specifics, elevate to implementation standard document

---

## Additional External Reviews

### Reviewer 5 Findings

## Quality Issues
* **[Principle 1.2]**: Unclear boundary between zero-assumption design and framework conventions. Prescribing hardcoded tool-specific names (e.g., `Devin-Adapter.py`) in example sub-principles contradicts the core mandate of generic applicability in Principle 1.3.
* **[Principle 8.3]**: Poorly defined architectural requirement. Mandating that every file contain its own copy of helper and logging utility functions rather than sharing modules creates extreme code duplication, breaking standard software engineering practices (DRY) and introducing maintenance drift.
* **[Principle 9.1]**: Vague log management specification. Directing every file to write to individual per-file log targets (e.g., `Protocol-Log-DATE.jsonl`) creates fragmented log files without defining how they aggregate into the centralized, tamper-evident hash chain defined in Principle 22.
* **[Principle 13 to 23 Sub-numbering]**: Numbering hierarchy inconsistency across multiple principles. Principles 17, 18, 19, 20, 22, and 23 use mismatched sub-principle numbers (e.g., Principle 17 uses sub-numbers `13.1`–`13.4`, Principle 18 uses `14.1`–`14.4`, Principle 22 uses `18.1`–`18.4`, and Principle 23 uses `19.1`–`19.4`).

## Contradictions
* **[Principle 19.1] vs [Principle 26.2]**: Principle 19.1 requires the framework to fail-open ("default to allow" when a hook fails to maintain system uptime), whereas Principle 26.2 enforces a fail-closed design ("block unknown or failed governance checks"). Industry standards for security-critical AI controls (such as the Agent Control Standard) enforce inline fail-closed semantics to prevent unauthorized execution during control plane failures.
* **[Principle 20.1] vs [Principle 26.2]**: Principle 20.1 specifies that default system installation operates in non-blocking advisory mode (log-only), while Principle 26.2 states that the governance layer is in-path and fail-closed by default.
* **[Principle 8.3] vs [Principle 11.1 & 12.1]**: Principle 8.3 forbids files from relying on shared helper functions and requires duplicated logic across files, directly violating Principle 11.1 (Single Responsibility Principle) and Principle 12.1 (Loose Coupling / Modular Separation).
* **[Principle 18.1] vs [Principle 13.2 & 22.1]**: Principle 18.1 targets sub-0.1ms hook latency for allow paths, which conflicts with Principle 13.2 (executing Python scripts synchronously per hook) and Principle 22.1 (calculating cryptographic hash chains and signatures inline per log entry). Inline cryptographic signing and synchronous script invocation typically incur latencies well beyond 0.1ms.

## Missing Principles
* **Agent Identity & Context Boundary Binding**: The framework lacks an explicit principle governing principal identity propagation (linking user identities, agent identities, and dynamic session contexts to tool calls). Standard governance frameworks (e.g., ISO/IEC 42001 and Agent Control Standard) require explicit subject-predicate-object identity verification before policy evaluation.
* **Memory & Context Window Protection**: Overseer covers tool usage interception but lacks architectural principles for inspecting or isolating agent memory reads/writes and context store operations. As highlighted in agent control frameworks (e.g., ACS), intercepting memory operations is necessary to protect against prompt injection and memory corruption attacks.

## Overall Assessment
The Overseer Framework Architecture Principles present a comprehensive foundation for hook-based AI agent interception, but the document suffers from operational contradictions between strict security (fail-closed) and high availability (fail-open/advisory), alongside minor sub-numbering defects and unmaintainable modularity constraints.

---

### Reviewer 6 Findings

## Quality Issues
**[Principle 17]**: Numbering error – sub-principles start at 13.1 instead of 17.1 (copy-paste from Principle 13). Same issue appears in Principles 18 (14.x), 19 (15.x), and 20 (16.x). Breaks referential integrity and testability.

**[Principle 1.1 / 1.4 / 6]**: "Zero hardcoded event types" + "dynamic discovery" is clear in intent but lacks a concrete contract for *how* discovery occurs or what happens on discovery failure. Actionability is reduced; teams cannot reliably decide whether a given implementation upholds or violates the principle.

**[Principle 8.3 / 8.4]**: "Each file contains all the functionality it needs" and "no helper functions in other files" conflicts with normal modular design and Principle 10 (KISS) / Principle 11 (SOLID). Extreme interpretation produces duplicated utilities and hurts maintainability. Not robust under TOGAF "robust" criterion.

**[Principle 9]**: "Extremely verbose logging" of every entry/exit/parameter is stated without quantitative bounds. Directly tensions with Principle 18 performance targets (<0.1 ms p50). No guidance on sampling, levels, or hot-path cost.

**[Principle 20 vs 26]**: "Advisory by default / log-only" (20) vs "Fail-Closed Default" (26.2) are both declared as desired state without explicit precedence or configuration model. Ambiguous which wins on first install or under policy-evaluation failure.

**[Principle 15]**: Bypass menu is well-motivated but lacks statement of when the menu itself is subject to meta-rules or enterprise disablement. Edge-case handling (non-interactive environments, CI, headless) is undefined.

**[Principle 25.3]**: "Declarative policy" is good, yet the document also hard-wires YAML + accompanying Python files (Principle 13). The tension between pure declarative engines (Cedar/OPA) and Python execution files is not resolved.

## Contradictions
**[Principle 20] vs [Principle 26]**: Light/advisory-by-default vs fail-closed/in-path enforcement.  
Web confirmation: Security literature (fail-closed vs fail-open analyses, AI-gateway design notes) treats the choice as a deliberate, risk-tiered trade-off, not simultaneous defaults. The document asserts both without a resolution mechanism or workload classification.

**[Principle 9] vs [Principle 18]**: Extremely verbose per-operation logging vs sub-millisecond hook budgets and <1 % CPU overhead.  
Web confirmation: High-frequency interception points (hooks, gateways) routinely use sampling or structured minimal logs precisely to stay inside latency SLOs; unconstrained verbosity is known to violate the performance targets claimed here.

**[Principle 1 / 4 / 6] (true agnosticism, open strings, zero assumptions) vs [Principle 3] (config-driven adapter selection) and file-system conventions**: Agnosticism is absolute, yet concrete directory layouts, naming (`[ApplicationName]-Adapter.py`), and config keys are prescribed.  
Acceptable as organizational convention, but the absolute language in 1/4/6 makes the conventions look like violations.

**[Principle 8] (extreme file independence, own utilities) vs [Principle 10 / 11 / 12] (KISS, SOLID, component modularity)**: Duplication of logging and helpers is required by 8 while forbidden by the others.  
Web confirmation: TOGAF principle-quality criteria and standard modular-design literature treat such extreme isolation as anti-pattern once it increases cognitive load or maintenance cost.

**[Principle 13 / 16] (YAML + Python action files) vs [Principle 27] (pluggable declarative engines such as Cedar/OPA)**: Python execution files embed procedural logic; pure declarative engines are preferred for scale and auditability. No adapter or abstraction layer is defined to reconcile them.

## Missing Principles
**Agent Identity & Least Privilege**: Every surveyed agent-governance architecture (Microsoft Agent Governance Toolkit, AWS agentic guidance, TURION six-layer model, COMPEL, ISO/IEC 42001 mappings) treats distinct, short-lived, scoped agent identities as foundational. Overseer covers tool hooks and roles in the delegation chain (30) but never states an identity principle for the agent itself.

**Kill-Switch / Instant Revocation**: Runtime "stop everything" capability appears in multiple 2025–2026 frameworks (Agent SRE packages, seven-pillar models, Layered Governance Architecture). Absent here; only per-action blocks and bypass menus exist.

**Human-in-the-Loop Escalation Gates (beyond bypass)**: Principle 29 mentions pre-deployment human accountability and Principle 15 offers post-block bypass, but there is no principle for configurable approval gates on high-impact actions *before* they reach the tool (common in supervised-agency scopes and NIST-aligned guidance).

**Risk Tiering / Scope Classification**: AWS and public-sector frameworks classify agents by autonomy/impact scope and apply graduated controls. Overseer has configurable strictness (20) but no explicit principle for classifying agents or workloads and binding different principle sets to different tiers.

**Supply-Chain / Plugin Trust for Adapters & Rules**: Principle 21 covers dependency installation; nothing addresses trust scoring, signing, or provenance of third-party adapters or user-supplied rule packages—explicitly called out in agent-marketplace and plugin-governance literature.

## Overall Assessment
The document is unusually comprehensive and aligns well with emerging agent-governance practice (in-path enforcement, deterministic verdicts, tamper-evident audit, delegation accountability). Quality is reduced by numbering errors, absolute language that creates internal contradictions (especially advisory vs fail-closed and logging vs performance), and a few missing first-class concerns (agent identity, kill-switch, risk tiering) that every comparable framework treats as non-negotiable. Tightening the absolute claims, resolving the default-mode conflict, and adding the identity/revocation principles would raise it from strong draft to production-grade architecture principles.

---

### Reviewer 7 Findings

## Quality Issues
[Principles 1, 3, 4, 6, 34]: **The abstraction boundary is internally unclear.** Principles 1/4/6 say the framework makes no assumptions and accepts arbitrary event/capability structures, while Principle 34 requires a canonical payload with fields such as `action_type`, `agent_identity`, and `resource`. Decide explicitly whether the canonical model is the **stable framework contract** and adapter-specific data is an extension, or whether Overseer is genuinely schema-agnostic. ACS similarly uses standardized runtime hooks/payload semantics rather than an entirely unconstrained event model.

[Principles 1.1, 6.1, 6.4]: **"ANY event type", "any string is valid", and "infinite extensibility" are too absolute.** Open identifiers provide extensibility, but the system still needs a defined contract for syntax, semantics, validation, compatibility, and security. "Any string is valid" is not a useful architectural decision criterion.

[Principle 4.3]: **"All framework behavior is configurable" is over-broad.** Security-critical invariants should not necessarily be configuration-controlled. Otherwise configuration becomes an alternate programming language and potentially an enforcement bypass.

[Principles 8.1–8.3]: **"Each file must be completely independent" is not a sound architectural principle.** It encourages duplicated utilities, excessive fragmentation, and fights normal modularity/DRY practices. Principle 8.3 explicitly says files should not rely on shared helper functions, which conflicts with Principles 7, 10, 11 and 12.

[Principle 9]: **"Extremely verbose" logging is not a sufficiently precise governance principle.** It lacks criteria for sensitive-data handling, log volume, retention, sampling, redaction, and operational cost. More importantly, 9.4 says logging may silently fail, which is problematic for a governance system whose auditability is a stated product objective.

[Principles 18.1–18.4]: **The numerical performance targets appear arbitrary and are not justified by a workload model.** `<0.1ms p50`, `<0.5ms p99`, `<1% CPU`, and "zero allocations" should be treated as benchmark targets, not architectural principles, unless backed by defined hardware, payload size, policy complexity, concurrency, and measurement methodology. For comparison, Cedar describes sub-millisecond-scale authorization performance but does not establish these targets as universal governance requirements.

[Principle 21.4]: **"Use packages published at least 7 days ago" is not an established supply-chain security control.** Age does not establish package integrity or safety. Replace it with provenance/integrity verification, dependency pinning, vulnerability monitoring, trusted registries, and controlled updates.

[Principle 25]: **"Binary outcomes (allow/deny/modify)" is conceptually inconsistent.** Three outcomes are not binary. More importantly, deterministic policy evaluation does not require all inputs to be deterministic; a policy engine can consume externally produced risk/classification signals. ACS explicitly describes allow/deny/modify as deterministic runtime verdicts.

[Principle 26]: **"Fail-closed by default" is too absolute without distinguishing enforcement failure from policy denial.** A security-sensitive action may appropriately fail closed, while availability-critical or advisory controls may have a different failure policy. NIST treats risk management as contextual rather than prescribing one universal failure behavior.

[Principle 29]: **The principle mixes organizational governance with architectural principles.** Risk assessment, human accountability and user education are valid governance requirements, but they sit at a different abstraction level from "plugin SDK" or "hook composability." ISO/IEC 42001 explicitly treats organizational AI management as a broader management system covering policy, risk, accountability and continual improvement.

[Principle 32]: **"Minimal context" needs a security exception for authorization/audit context.** The example of passing only a file path can be insufficient for authorization; identity, delegation chain, tenant, policy version, provenance and trust context may be security-critical. ACS and Cedar both make identity/context part of the authorization decision model.

[Principle 33]: **"Race conditions eliminated" is an unprovable absolute.** Stateless policy evaluation reduces one class of race condition but cannot eliminate races involving filesystem state, external resources, concurrent agents, or TOCTOU conditions.

[Numbering]: **Sub-principle numbering is broken from Principle 17 onward.** Principle 17 contains `13.1–13.4`; Principle 18 contains `14.1–14.4`; Principle 19 contains `15.1–15.4`; Principle 20 contains `16.1–16.4`; Principle 22 contains `18.1–18.4`; Principle 23 contains `19.1–19.4`. This makes references ambiguous and is a direct consistency defect.

## Contradictions
[Principle 19] vs [Principle 26]: **Fail-open vs fail-closed.** Principle 19 allows a failed hook to default to "allow"; Principle 26 requires failed governance checks to block. These are directly incompatible for the same enforcement mode.

[Principle 20] vs [Principle 26]: **Advisory/log-only by default vs fail-closed by default.** A fresh installation cannot simultaneously default to "don't block" and "block when governance cannot establish authorization." Resolve this through explicit **policy modes/risk tiers**, rather than contradictory global defaults.

[Principle 15] vs [Principle 26]: **Universal bypass vs fail-closed enforcement.** Principle 15 says blocks generate user override options, while Principle 26 says unknown/failed authorization is blocked. These can coexist only if the bypass is itself a separately authorized governance decision with defined scope, identity, expiry and audit requirements. NIST explicitly recognizes appeal/override as a governance mechanism, so the concept is valid; the document needs to define the security boundary.

[Principle 24] vs [Principle 33]: **Configurable hook ordering vs no ordering/temporal dependencies.** Principle 24 permits arbitrary configurable ordering; Principle 33 says decisions must not depend on ordering and claims temporal dependencies should not exist. If hooks are truly independent, order should be semantically irrelevant; if ordering matters, that dependency needs to be explicit.

[Principle 8] vs [Principles 7, 10, 12]: **File-level independence conflicts with modularity and simplicity.** "Each file contains its own utility functions" creates duplication, while the other principles promote stable interfaces, loose coupling and simple design.

[Principles 1/4/6] vs [Principle 34]: **Unconstrained schemas vs canonical schema.** A genuinely schema-agnostic framework cannot simultaneously require every hook to conform to a fixed canonical model. A better formulation is: *adapters normalize external events into a versioned canonical contract, while retaining extension fields.*

[Principle 25] vs [Principle 27]: **Not a hard contradiction, but significant redundancy.** Both establish declarative, deterministic policy evaluation. Principle 27 should probably become the policy architecture principle, while Principle 25 should define the decision semantics. OPA explicitly separates policy decision-making from enforcement, supporting that separation.

## Missing Principles
[**Least-Privilege Authorization**]: The document discusses tool access control and authority limits, but never establishes least privilege as a first-class architectural invariant. Agent permissions should be scoped to the minimum tools/resources required for the task, with runtime authorization. OWASP explicitly recommends least-privilege tool access, and Cedar models authorization around principal/action/resource/context.

[**Identity, Authentication and Trust Propagation**]: Principle 30 covers role propagation, but there is no foundational principle requiring authenticated, unambiguous identity for humans, agents, sub-agents, adapters and services. ACS treats agent identity as a first-class runtime control concern.

[**Policy Lifecycle and Change Control**]: There is no principle covering policy versioning, review, approval, rollback, compatibility, provenance or effective dates. This is a major omission for a governance system. ISO/IEC 42001 emphasizes maintaining and continually improving an AI management system, while NIST calls for continuous risk management and monitoring.

[**Policy Conflict Resolution / Precedence**]: The document says policies are composable but never defines what happens when policies disagree. A governance engine needs deterministic precedence semantics—e.g. deny-overrides-allow, explicit priority, or policy-combining algorithms. Cedar and OPA both provide explicit policy evaluation semantics rather than leaving conflicts undefined.

[**Configuration and Policy Integrity**]: You have tamper-evident *logs*, but not integrity protection for the policies/configuration that determine enforcement. A compromised rule, adapter, or configuration can undermine every audit guarantee. This should cover provenance, integrity verification, authorized change, rollback and potentially signing.

[**Secrets and Sensitive-Data Protection**]: There is no principle governing credentials, secrets, PII, sensitive tool arguments, or log redaction. This is especially important because Principles 9, 22 and 28 explicitly encourage extensive logging. Current agent-control guidance identifies credential governance and controlled data handling as core runtime concerns.

[**Incident Response / Emergency Disablement**]: There is no explicit kill-switch, quarantine, rollback or recovery principle. NIST's Manage function explicitly includes incident response, recovery, appeal/override and decommissioning; current agent-control standards also treat rapid disablement as a control requirement.

[**Continuous Evaluation and Assurance**]: Principle 29 handles pre-deployment risk, but the architecture lacks a principle requiring ongoing testing, red-teaming, regression testing and policy/control effectiveness measurement. NIST explicitly requires AI systems to be tested before deployment and regularly during operation, with continual improvement.

[**Agent / Tool Inventory and Supply-Chain Governance**]: The system governs adapters but does not establish an inventory of agents, tools, models, connectors, skills or capabilities. ACS specifically introduces an Agent Bill of Materials for this purpose, while its control model treats tools, credentials, memory and connectors as part of the governed boundary.

[**Context and Input Integrity**]: Principle 32 minimizes context, but there is no principle saying that supplied context, tool arguments, tool descriptions, memory and external content are untrusted and must not silently expand authority. This is important because agentic systems introduce prompt/context injection and tool-manipulation risks. OWASP recommends structural separation of trusted instructions from untrusted content and validation before high-impact execution.

## Overall Assessment
The document has a **strong runtime-control foundation**—agnostic adapters, centralized enforcement, declarative policy, auditability, runtime hooks, delegation and standardized payloads are all directionally aligned with current agent-control architecture.

The biggest problem is that it currently mixes **architectural principles, coding conventions, implementation prescriptions, product requirements, performance targets and organizational governance** into one list. The most urgent fixes are the **19/26 and 20/26 contradictions, 1/4/6/34 abstraction conflict, 24/33 ordering conflict, broken sub-numbering, and missing identity/least-privilege/policy-lifecycle/config-integrity/incident-response principles**.

---

### Reviewer 8 Findings

## Quality Issues
**[Principle 1.1]**: "Zero Hardcoded Event Types" claims the framework accepts "ANY" event types adapters provide, but this directly conflicts with **[Principle 34]** which mandates a "canonical model" (action_type, agent_identity, resource, access_level). If event types are completely open, how is the canonical model enforced? HookBus addresses this via "standardizing heterogeneous hook events into a standard JSON envelope," but Overseer's document does not explain how it balances these two demands.

**[Principle 13 vs 17]**: Duplicate numbering—both principles are labeled "13," breaking document integrity. TOGAF states principles must be "Consistent" (consistent numbering and structure), making this a direct violation of professional documentation standards.

**[Principle 17.1–17.4]**: These sub-principles are numbered 13.1–13.4, which do not match their parent principle (17). This appears to be a copy-paste error that undermines the document's professionalism.

**[Principle 2]**: "Overseer-Centric Architecture" claims hooks point to overseer.py as the "single integration point," but **[Principle 8]** "Extreme Modularization" demands that "each file is completely self-contained." A single integration point inherently creates coupling between files, contradicting "minimal connections" and "files can be moved without breaking dependencies." The document does not explain how to resolve this tension.

**[Principle 26]**: "Fail-Closed Default" requires "the system fails closed by default, blocking unknown actions," citing that "Default-deny is the only safe starting point." However, **[Principle 20]** "Light by Default, Advisory by Default" demands the "default governance mode is advisory (log only, don't block)." These are direct, opposing defaults.

**[Principle 31]**: "No Silent Failures" requires "denials are immediately surfaced to the user," but **[Principle 9.4]** "Silent Failure Pattern" explicitly demands that "logging failures don't crash the system"—adopting a silent-failure approach. Although they address different concerns (user notification vs. logging reliability), the naming conflict creates implementation confusion.

**[Principle 3.2]**: "Adapter-Specific Hook Mapping" claims "hooks are determined by the selected adapter," yet **[Principle 1.1]** demands the "framework accepts ANY event type adapters provide." If the framework accepts any event type, why must the adapter "determine" hooks? This implies an unresolved tension between capability discovery and framework agnosticism.

**[Principle 4.2]**: "Metadata-Driven Processing" requires the "framework uses metadata to determine how to process events," but does not define the metadata schema. Without a standardized metadata format, "metadata-driven" is unenforceable. The Herd framework employs explicit "execution-agnostic roles, authority models," while Overseer's approach lacks similar specificity.

**[Principle 25.2]**: "State-Based Rule Matching" requires "rules match against explicit state, not probabilistic analysis," but does not define what constitutes "state." Is it the entire system state, specific event context, or rule-specific state? This ambiguity makes the principle untestable. Industry practice dictates "moving critical rules out of the prompt and into deterministic hooks the model cannot override"—Overseer should similarly concretize what "state" means.

**[Principle 28]**: "Runtime Observability Through Hooks" lists monitoring, cost tracking, compliance auditing, and performance profiling, but does not specify how observability data integrates with **[Principle 22]** "Tamper-Evident Audit" (cryptographic hash chains). Observability logs and tamper-evident audit logs are different concerns, and the document does not clarify whether they share storage. "Audit by design: Every interaction produces a structured, correlated trace automatically" is an industry standard—Overseer does not specify the structured format of its audit trail.

**[Principle 33]**: "Stateless Enforcement" requires "each hook invocation is independently decidable," but **[Principle 24.1]** "Hook Chaining" requires "multiple hooks can be chained together." If hooks are chained, they inherently have order and potential dependencies, contradicting "no cross-hook dependencies." HookBus employs a "priority-weighted deny-wins algorithm" to handle multiple subscribers—a pragmatic approach, but Overseer does not explain how it resolves conflicts in composition.

**[Principle 32]**: "Minimal Context Passing" requires "pass only what the enforcement rule needs," but **[Principle 34]** "Standardized Hook Payloads" requires "all hooks have action_type, agent_identity, resource, access_level." A standardized payload inherently includes fields that some hooks may not need—"minimal" and "standardized" are in inherent tension.

**[Principle 6.1]**: "Open String Identifiers" requires "any string is valid," yet **[Principle 34.1]** mandates a canonical model with standard fields such as action_type, agent_identity, and resource. The tension between open-string identifiers and mandatory canonical fields is unresolved. ACS returns "allow, deny, modify" verdicts at "execution checkpoints"—these are limited, predefined outcome types, not open strings. This indicates the industry favors bounded types over complete openness.

## Contradictions
**[Principle 26] vs [Principle 20]**: Fail-Closed vs Advisory Default. Principle 26 requires "the system fails closed by default, blocking unknown actions" and explicitly cites "Default-deny is the only safe starting point." Principle 20 requires "the default governance mode is advisory (log only, don't block)." These directly conflict on default behavior. If the system defaults to advisory, it cannot achieve fail-closed. Web search confirms: industry standards explicitly support default-deny. "Default-deny" is listed as a primary principle of accountable AI agent networks. Aegis states "secure defaults: block catastrophic, irreversible actions with zero configuration"—indicating industry practice leans toward security-first, not advisory-first.

**[Principle 1.1] vs [Principle 34]**: Zero Hardcoded Event Types vs Standardized Hook Payloads. Principle 1.1 demands the framework accept "ANY event type" with no predefined types. Principle 34 demands a canonical model where "all hooks have action_type, agent_identity, resource, access_level." If event types are fully open, canonical fields cannot be enforced. If canonical fields are mandatory, event types are not fully open. This is a fundamental architectural contradiction. Web search indicates the industry resolves this via "standardizing heterogeneous hook events into a standard JSON envelope"—i.e., keeping event types open but defining a standard envelope format. Overseer does not adopt this approach, instead demanding both complete openness and complete standardization.

**[Principle 8] vs [Principle 2]**: Extreme Modularization vs Overseer-Centric. Principle 8 requires "each file is completely self-contained" and "connections between files are minimized." Principle 2 requires "hooks point to overseer.py as the primary integration point" and "overseer.py coordinates all governance decisions." A single integration point inherently creates dependencies on overseer.py, conflicting with "minimal connections" and "files can be moved without breaking dependencies." Web search confirms that a hub-and-spoke model (all hooks flowing through a single dispatcher) is a hook-system best practice—but this does create centralized dependency. Principle 8's "file independence" is at odds with this pattern, and the document provides no balancing guidance.

**[Principle 10] vs [Principle 9]**: KISS vs Comprehensive Logging. Principle 10 favors "simple solutions" and "functions under 50 lines." Principle 9 requires "log every significant operation" with "extremely verbose and detailed" logs. Extremely detailed logging adds code complexity (additional logging calls per function), conflicting with KISS simplicity. This is a manageable tension, but the document does not acknowledge it or provide balancing guidance.

**[Principle 4.1] vs [Principle 34]**: Generic Container Pattern vs Standardized Payloads. Principle 4.1 demands the framework be a "generic container" with "generic interfaces that work with any data structure." Principle 34 demands a "canonical model" with specific fields. A generic container should not care about specific data structure fields, whereas a canonical payload demands specific fields. This is a fundamental design philosophy conflict.

**[Principle 3.2] vs [Principle 1.3]**: Adapter-Specific Hooks vs Zero CLI-Specific Assumptions. Principle 3.2 requires "hooks are determined by the selected adapter." Principle 1.3 requires the "framework is completely CLI-agnostic." If hooks are determined by the adapter, the framework must understand adapter hook capabilities, conflicting with "zero adapter-specific logic" (Principle 1 success criteria).

**[Principle 24.1] vs [Principle 33.1]**: Hook Chaining vs Independent Hook Decisions. Principle 24.1 requires "multiple hooks can be chained together." Principle 33.1 requires "each hook invocation is independently decidable" and "hook decisions don't depend on previous hook results." If hooks are chained, they have an order and potential dependency, contradicting "independently decidable." Web search shows HookBus uses a "priority-weighted deny-wins algorithm" to merge decisions from multiple subscribers—acknowledging that coordination among multiple hooks is necessary, contradicting strict independence.

## Missing Principles
**[Principle: Least Privilege and Permission Boundaries]**: The document does not define what permissions agents should have, how they are granted, or how permission boundaries are enforced. Principle 30 discusses "delegation chain accountability" but does not address how permission boundaries are established in the first place. Industry standards require "Attribute-based policy: Policies reference agent attributes, not agent names" and "Zero-trust identity: Every request authenticated." NIST AI RMF mandates "Establish organizational structures, policies, accountability mechanisms." Overseer lacks a core principle on agent authentication, authorization, and least privilege. Aegis assumes "agents are untrusted at the point of action"—Overseer does not clarify its trust model.

**[Principle: Testability and Verifiability]**: Although testability appears in success criteria ("each layer is independently testable"), there is no principle about how the architecture itself should support testing. Enterprise architecture standards mandate "Testability: Architecture that enables comprehensive automated testing." TOGAF requires principles to be "Robust - Enable good decisions about architectures and plans, enable enforceable policies and standards to be created." Overseer lacks principles on how to verify rule correctness, test hook behavior, or simulate governance decisions. "Dependency-aware execution" and "Real-time execution oversight" are key criteria in agent governance scorecards—Overseer should clarify its testability approach.

**[Principle: Secure Supply Chain and Dependency Management]**: Principle 21 covers dependency installation but misses broader supply chain security—such as vulnerability scanning, SBOM generation, or dependency update policies. ACS includes "Inspect extends CycloneDX, SPDX, and SWID to produce dynamic Agent Bills of Materials"—Overseer lacks a principle on software bill of materials or dependency transparency. "In governed systems, evolution must be auditable, changes must be attributable, and rollback"—Overseer should clarify how its dependency management supports these requirements.

**[Principle: Human Intervention and Calibrated Trust]**: The document discusses bypass menus (Principle 15) and human accountability (Principle 29.2), but lacks a principle on *when* human approval is required, *how* humans intervene, and *how* human approval coordinates with automated enforcement. "Human-in-the-Loop (Calibrated Trust)" is a standard component of agent governance scorecards. ACS policies can "mask sensitive information or request human approval." Industry practice shows "rules are binary—commands either violate or they don't"—but certain decisions require human judgment. Overseer lacks a guiding principle for triggering human intervention. The EU AI Act mandates "demonstrable human oversight of high-risk AI systems, including the ability to intervene in real time"—Overseer should clarify its support for real-time human intervention.

**[Principle: Backward Compatibility and Versioning]**: Principle 5.3 discusses SDK versioning, but there is no principle on backward compatibility for the framework itself, rule formats, or hook contracts. As the system evolves, old rules and adapters should continue to work. HookBus is "event-type agnostic, hot-reloadable, transport-independent, and stateless"—these features support evolution. Overseer should clarify its versioning strategy and deprecation policy. TOGAF requires "Stability"—Overseer lacks an explicit principle on stability and backward compatibility.

**[Principle: Zero-Trust Architecture]**: The document does not adopt zero-trust principles. "Zero-trust identity: Every request authenticated, every identity verified" is an industry standard. Overseer describes intercepting agent tool usage but does not specify how agent identity is verified, how identity spoofing is prevented, or how requests are validated as coming from a trusted source. Aegis detects "rogue agent sessions (unidentified processes claiming agent names without valid cryptographic tokens)"—Overseer should clarify its zero-trust approach.

**[Principle: Observability-Driven Adaptation]**: Principle 28 covers observability, but only as passive monitoring. There is no principle on how observability data feeds back into governance decisions. The Herd framework includes "ability to learn from its own process." Industry discussions mention "adaptive guardrails"—"an overseer agent that adjusts safety policies based on what's actually happening." Overseer lacks a principle on how the governance system learns from or adapts to observability data.

## Overall Assessment
The document contains 34 principles with broad coverage, but suffers from **significant internal contradictions** (especially fail-closed vs advisory default, zero hardcoded event types vs standardized payloads, and extreme modularization vs centralized integration point), along with **critical gaps** (permission boundaries, testability, zero-trust, human intervention, backward compatibility, and observability-driven adaptation). Principle quality is uneven—some are specific and actionable (e.g., Principle 9 on logging, Principle 22 on tamper-evident audit), while others are overly abstract (e.g., Principle 4 on zero-assumption framework lacks concrete implementation guidance). **Numbering errors** (duplicate Principle 13) and **mismatched sub-principle numbering** undermine professional credibility. Recommend prioritizing resolution of core contradictions, supplementing missing security and governance principles, and adding concrete implementation guidance for abstract principles.

---

### Reviewer 9 Findings

## Quality Issues
**[Principle 17]**: Sub-principles are incorrectly numbered 13.1–13.4 (copy-paste error from earlier version). Should be 17.1–17.4.

**[Principle 18]**: Sub-principles are incorrectly numbered 14.1–14.4 (same copy-paste error). Should be 18.1–18.4.

**[Principle 25 intro]**: References "Agent Control Standard, SkillGuard, ThumbGate, SteerPlane, Microsoft Agent Governance Toolkit" as competitive benchmarks. Web search finds no evidence these exist as recognized standards or products. Only "Agent Control" (Galileo, March 2026) appears as a product, not a standard. Citing fictional competitors undermines credibility.

**[Principle 1.1]**: "Zero Hardcoded Event Types" claims the framework accepts ANY event type without modification. This is unactionable—without any structural contract, the framework cannot validate, route, or process events. Testability is impossible: how do you verify a system handles "anything" correctly?

**[Principle 4]**: "Zero-Assumption Framework" is architecturally unachievable. Any system that processes data must assume some structure (e.g., existence of a "type" field for metadata-driven routing per 4.2). The principle contradicts itself within its own sub-points.

**[Principle 20]**: "Advisory by Default" lacks a clear escalation path. It states default is log-only but does not define what triggers transition to blocking mode, making it untestable in practice.

**[Principle 26]**: "Fail-Closed Default" is clear and actionable, but directly contradicts Principle 20. A system cannot simultaneously default to log-only (advisory) and fail-closed (block).

**[Principle 33]**: "Stateless Enforcement" claims each hook invocation is independently decidable with no cross-hook dependencies. This is untestable because Principle 30 (Delegation Chain Accountability) explicitly requires cross-hook state propagation.

## Contradictions
**[Principle 20] vs [Principle 26]**: Principle 20 demands "Advisory Mode Default" (log-only, don't block), while Principle 26 demands "Fail-Closed Default" (blocks unknown actions). These are mutually exclusive security postures. Web search confirms fail-closed is the security best practice for access control and authorization systems: "A fail-closed state ensures that, in the event of an error, access is denied, maintaining the integrity of your application's security" and "failing closed ensures that applications deny access during unexpected failures, thereby maintaining security integrity." Advisory mode is a deployment maturity choice, not a secure default.

**[Principle 1.1] vs [Principle 34]**: Principle 1.1 requires "Zero Hardcoded Event Types" (accept ANY event type), while Principle 34 requires "Standardized Hook Payloads" with a canonical model containing mandatory fields like `action_type`, `agent_identity`, `resource`, `access_level`. If the framework enforces a canonical payload structure, it is by definition making hardcoded assumptions about event types and fields.

**[Principle 4] vs [Principle 34]**: Principle 4 states the framework makes "no assumptions about...event structures" and provides "generic interfaces that work with any data structure." Principle 34 mandates a canonical payload model with specific required fields. A system cannot be simultaneously structure-agnostic and canonically structured.

**[Principle 15] vs [Principle 26]**: Principle 15 requires bypass menus allowing users to override blocks, while Principle 26 requires fail-closed behavior where "if governance check fails, action is blocked." A fail-closed system with default bypass menus is effectively fail-open by user override, defeating the security intent.

**[Principle 33] vs [Principle 30]**: Principle 33 requires "no cross-hook dependencies" and "each hook invocation independently decidable," while Principle 30 requires "Role Propagation" and "Chain of Custody" tracking across delegation chains. Delegation accountability inherently requires state to propagate across multiple hook invocations (e.g., PreToolUse → tool execution → PostToolUse), violating statelessness.

**[Principle 32] vs [Principle 30]**: Principle 32 demands "Minimal Context Passing" (only pass what enforcement needs), while Principle 30 requires full "Chain of Custody" tracking across delegation layers. Tracking a complete delegation chain requires passing substantial context (orchestrator identity, sub-agent scope, API bounds, original user role), directly conflicting with minimal context.

## Missing Principles
**Agent Identity and Authentication**: NIST's AI Agent Standards Initiative and Microsoft both emphasize that "every agent must be observable, governed, and secure" requiring "a single identity for every agent" with agent-as-principal identity management. The document has no principle requiring unique agent identity or authentication.

**Risk-Based Classification / Tiered Governance**: The IAPP three-tier guardrail framework and NIST agentic profiles recommend tiering agents by risk level (standard, agentic-specific, context-specific). The document lacks any principle for risk classification or tiered enforcement, which is essential for scaling from hobbyist to enterprise.

**Human-in-the-Loop / Human Oversight**: NIST AI RMF, EU AI Act, and Microsoft Responsible AI principles all require human oversight for high-risk autonomous actions. The document mentions bypass menus for users but has no principle mandating human approval gates for high-risk actions.

**Prompt Injection and Tool Misuse Defense**: OWASP ranks prompt injection as the #1 vulnerability for AI agents, and NIST research found novel attack strategies achieved an 81% success rate against baseline defenses. No principle addresses input validation or prompt injection defenses despite being the primary attack vector.

**Least Privilege / Zero Trust**: The Cloud Security Alliance Agentic Trust Framework defines core elements including "Segmentation: Where can you go?" and "Identity: Who are you?" based on Zero Trust principles. The document lacks a principle for least-privilege access or Zero Trust architecture, which is foundational to modern agent governance.

**Policy Versioning and Rollback**: For a config-driven system (Principle 3), there is no principle addressing policy versioning, atomic updates, or rollback capabilities. Fleet-wide policy updates without versioning are operationally dangerous—Galileo's Agent Control and other control planes emphasize "hot-reloadable rules" with version safety.

**Explainability and Transparency**: While logging is comprehensive (Principle 9), there is no principle requiring governance decisions to be explainable or interpretable. The EU AI Act and NIST AI RMF mandate transparency for high-risk AI systems.

## Overall Assessment
The document covers an impressive breadth of architectural concerns but suffers from critical contradictions—most notably between advisory-by-default and fail-closed security—and contains unverifiable competitive references. The numbering errors and structural inconsistencies suggest insufficient editorial review. The framework would benefit from resolving the security posture contradiction and adding principles for agent identity, risk tiering, and human oversight that align with emerging NIST and EU standards.

---

### Reviewer 10 Findings

## Quality Issues
[Principle 17, 18, 19, 20, 22, 23]: Sub-principle numbering is incorrect. Principle 17 contains 13.1-13.4; Principle 18 contains 14.1-14.4; Principle 19 contains 15.1-15.4; Principle 20 contains 16.1-16.4; Principle 22 contains 18.1-18.4; Principle 23 contains 19.1-19.4. This breaks the document's internal consistency.

[Principle 8.3 & 9.1]: Mandating that "each file should not rely on helper functions in other files" and "each file implements its own logging function" is a severe anti-pattern. It violates the DRY (Don't Repeat Yourself) principle, reduces maintainability, and prevents the use of standard tooling (e.g., Python's built-in `logging` module). This should be refactored to mandate shared, standard observability libraries.

[Principle 21.4]: Dictating that packages "must be published at least 7 days ago" is a specific supply chain implementation tactic, not an architectural principle. It should be abstracted to a principle like "Dependency Vetting and Provenance Verification."

[Principle 29]: "Governance Before Deployment" describes an operational workflow (risk assessment, human approval processes) rather than an architectural property of the software system. It belongs in an operational runbook, not an architecture principles document.

## Contradictions
[Principle 26.2] vs [Principle 19.1]: Direct contradiction in failure modes. P26.2 ("Fail-Closed Default") states that if a governance check fails, the action is blocked. P19.1 ("Graceful Degradation") states that if a hook fails, it defaults to "allow" (fail-open). These cannot coexist. - [Web search confirmation: "Fail-closed vs fail-open security" confirms these are mutually exclusive paradigms. Fail-closed blocks access on security mechanism failure, while fail-open permits access.]

[Principle 9.2] vs [Principle 18.1]: Implicit contradiction in performance. P9.2 demands "Extremely Verbose Logging" (logging entry/exit, parameters synchronously to JSONL files). P18.1 demands "<0.1ms p50" hook execution time. Synchronous file I/O for verbose logging will consistently exceed sub-millisecond latency. - [Web search confirmation: "Python synchronous file I/O latency" confirms unbuffered synchronous file writes typically take 1-10ms+, fundamentally violating sub-millisecond requirements.]

[Principle 33] vs [Principle 22.1]: Implicit contradiction regarding state. P33 ("Stateless Enforcement") demands no temporal state dependencies and independent hook decisions. P22.1 ("Hash Chain Verification") requires generating a hash of the previous log entry, inherently requiring sequential state to compute the current entry. - [Web search confirmation: "Hash chain implementation state" confirms generating linked hash chains requires accessing the previous block's state.]

[Principle 10 (KISS)] vs [Principle 22.2]: Tension area. P22.2 demands "Cryptographic Signatures" for critical decisions using private/public keys. Managing PKI infrastructure for an embeddable, lightweight framework (P17) adds massive complexity, directly conflicting with the KISS principle. - [Web search confirmation: "PKI management complexity in software architecture" highlights significant key management and rotation overhead unsuitable for lightweight, local-first tools.]

## Missing Principles
[Policy Immutability and Separation of Duties]: The document lacks a principle ensuring that the governed AI agent cannot modify its own governance rules, meta-rules, or audit logs. If an agent can write to `/rules` or log files, it can bypass governance entirely. - [Web search confirmation: "Policy as code immutability" and NIST SP 800-53 "Separation of Duties" mandate that the entity being governed must be strictly separated from the entity managing the policies.]

[Privacy and Data Minimization in Audit]: While P32 mentions minimal context passing, there is no principle addressing PII or secret redaction in audit logs. P9.2 mandates logging "parameter values," which risks exposing credentials or personal data in plaintext. - [Web search confirmation: "NIST AI RMF" and "ISO/IEC 42001" emphasize privacy and data governance as core requirements, requiring explicit controls for data minimization and PII redaction in telemetry.]

[Explainability of Governance Decisions]: P31 mentions contextual error messages for denials, but lacks an architectural principle requiring the system to provide a human-readable, explainable rationale for why a specific policy was matched (e.g., policy decomposition). - [Web search confirmation: "AI governance explainability standards" (e.g., EU AI Act, NIST AI RMF) require that automated decisions be explainable and auditable, not just blocked.]

## Overall Assessment
The document provides a comprehensive and ambitious vision for a hook-based governance system, but suffers from critical internal contradictions between desired performance metrics (sub-millisecond latency, statelessness) and functional requirements (verbose synchronous logging, hash-chained audits). Addressing these technical trade-offs and separating true architectural principles from operational processes will significantly improve the document's clarity and applicability.