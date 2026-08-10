# Subagent Orchestration Guidelines

This document provides detailed guidance for implementing the Overseer Framework workflow using modern AI agent subagent capabilities for parallel execution and complex orchestration.

## When to Use Parallel Execution

Use parallel execution for independent tasks that can run simultaneously without dependencies:

- **Independent analysis tasks** (risk classification + boundary definition)
- **Multi-domain research** (technical + compliance + security analysis)
- **Validation across different dimensions** (code quality + compliance + dependencies)
- **Testing across different types** (unit + integration + security + performance)
- **Complex review requiring specialized expertise** (architecture + security + compliance)

**Use sequential execution for:**
- Tasks with clear dependencies (implementation before testing)
- Tasks requiring shared state or resources
- Tasks where order matters for correctness

## Subagent Selection Strategy

### Built-in Subagent Profiles

**Use `subagent_explore` for:**
- Research and codebase exploration tasks
- Documentation analysis
- Best practices research
- Dependency mapping

**Use `subagent_general` for:**
- Implementation and general development tasks
- Code writing and refactoring
- Standard development workflows
- Multi-step implementation tasks

### Custom Subagent Profiles

Create custom profiles for specialized domains:

**Risk Analysis Profile:**
- System prompt focused on security risk assessment
- Tools: vulnerability scanners, dependency analyzers
- Use for: security reviews, risk classification

**Compliance Validation Profile:**
- System prompt focused on regulatory compliance
- Tools: compliance checkers, policy validators
- Use for: GDPR/HIPAA compliance, regulatory review

**Code Quality Profile:**
- System prompt focused on code standards
- Tools: linters, formatters, static analyzers
- Use for: code quality validation, standards compliance

### Execution Mode Selection

**Background Mode:**
- Use for independent parallel tasks
- Parent agent continues working
- Automatic denial of unapproved tools
- Subagent notifies parent on completion

**Foreground Mode:**
- Use for dependent tasks requiring coordination
- Parent agent waits for subagent completion
- Manual approval of tool calls
- Direct result access

## Result Synthesis Methodology

### Parallel Completion Coordination

1. **Wait for completion**: Parent agent must wait for all parallel subagents to complete before synthesis
2. **Collect results**: Gather all subagent outputs with execution metadata
3. **Validate completeness**: Ensure all expected subagents completed successfully

### Conflict Detection and Resolution

**Compare subagent results for:**
- Contradictory findings (e.g., one says "safe", another says "risky")
- Overlapping recommendations with different approaches
- Missing or incomplete information
- Inconsistent risk assessments

**Conflict resolution strategy:**
1. **Prioritize by risk level**: Security/compliance findings take precedence
2. **Escalate conflicts**: When uncertain, flag for human review
3. **Document decisions**: Record conflict resolution rationale in audit trail
4. **Preserve findings**: Keep all critical findings even if contradictory

### Unified Summary Creation

**Synthesis requirements:**
- Preserve all critical findings from all subagents
- Remove redundant information while keeping unique insights
- Create clear prioritization of issues (critical > high > medium > low)
- Include synthesis methodology and any conflicts encountered
- Provide actionable next steps based on combined analysis

## Cost Management Principles

### Risk-Based Subagent Limits

**Low Risk Tasks (2-3 subagents maximum):**
- Routine bug fixes
- Standard feature implementations
- Documentation updates
- Configuration changes

**Medium Risk Tasks (4-6 subagents when justified):**
- New feature development
- Security fixes
- Performance improvements
- Integration work

**Critical Risk Tasks (7+ subagents + managed Devins):**
- Major architectural changes
- Security infrastructure updates
- Compliance overhauls
- Production deployments

### Cost Monitoring

**Implement cost controls:**
- Monitor subagent spend in real-time
- Set cost thresholds for each workflow phase
- Halt execution if costs exceed expected benefits
- Use cost monitoring data to optimize future workflows

**Cost-benefit analysis:**
- Evaluate parallel execution benefits vs. additional cost
- Consider sequential execution for marginal parallel benefits
- Document cost decisions in audit trail

## Iteration Loop Handling

### Maximum Iteration Limits

**Per evaluation gate:**
- Maximum 3 iterations before hard stop
- Each iteration must provide specific, actionable feedback
- Document iteration history with reasoning

**Iteration escalation:**
- **Iteration 1 failure**: Retry with specific feedback
- **Iteration 2 failure**: Escalate to higher-level review
- **Iteration 3 failure**: Hard stop, require human intervention

### Iteration Documentation

**Record in audit trail:**
- Iteration number and timestamp
- Failure reason and specific feedback
- Changes made between iterations
- Final outcome and justification

### Quality Improvement Focus

**Use iteration loops for:**
- Code quality improvements
- Test coverage enhancements
- Security vulnerability fixes
- Compliance gap remediation

**Do not use iteration loops for:**
- Scope changes or new requirements
- Architectural redesigns
- Fundamental approach changes

## Error Recovery for Subagent Failures

### Failure Classification

**Transient failures** (retry with same approach):
- Network timeouts
- Temporary resource unavailability
- Rate limiting
- Minor API errors

**Systematic failures** (change approach):
- Subagent profile mismatch
- Tool access issues
- Permission problems
- Resource constraints

**Critical failures** (escalate immediately):
- Security compromises
- Data corruption
- Resource exhaustion
- Unauthorized access attempts

### Recovery Strategies

**For transient failures:**
- Log failure with timestamp and error details
- Retry with exponential backoff (max 3 attempts)
- If retries fail, escalate to systematic failure handling

**For systematic failures:**
- Log failure with root cause analysis
- Attempt with different subagent profile or approach
- If alternative fails, escalate to human review

**For critical failures:**
- Immediately halt workflow execution
- Escalate to human review with full context
- Document failure in audit trail with security implications
- Do not attempt automatic recovery

### Learning from Failures

**Document in audit trail:**
- Failure patterns and recurrence
- Successful recovery strategies
- Subagent profile effectiveness
- Workflow optimization opportunities

**Use for improvement:**
- Update subagent profile selection guidelines
- Refine error classification criteria
- Improve failure detection and prevention
- Optimize cost management thresholds

## Governance Enforcement Integration

### Hook-Based Enforcement

**Use existing Overseer hooks at:**
- **Phase transitions**: Prevent advancement without proper completion
- **Subagent spawning**: Validate subagent selection and configuration
- **Result synthesis**: Ensure synthesis follows governance rules
- **Evaluation gates**: Enforce iteration limits and escalation

### State Machine Tracking

**Track both parent and subagent states:**
- Parent agent workflow phase
- Active subagents and their states
- Subagent completion status and results
- Evaluation gate iterations and decisions

**State machine responsibilities:**
- Enforce phase transition rules
- Track iteration limits
- Record state changes in audit trail
- Provide state for audit reconstruction

### Audit Trail Requirements

**Capture for all workflow steps:**
- Workflow phase transitions with timestamps
- Subagent spawning, execution, and completion
- Evaluation gate checks, iterations, and decisions
- User approvals with evidence reviewed
- Synthesis decisions and conflict resolution
- Cost monitoring and threshold breaches
- Error recovery attempts and outcomes

### Proof Bundle Enhancement

**Include parallel execution provenance:**
- Subagent execution timeline and coordination
- Resource usage and cost allocation
- Decision points and synthesis rationale
- Iteration history and escalation decisions
- Conflict resolution and recovery actions

## Skill Orchestration Pattern

### Orchestrator Skill Structure

**Create skills that:**
- Define subagent tasks and profiles
- Specify execution mode (background/foreground)
- Set success/failure criteria
- Handle result synthesis and decision logic
- Implement iteration loops and escalation

### Skill Frontmatter Configuration

```yaml
---
name: parallel_research
description: "Execute parallel research using subagents"
subagent: subagent_explore
mode: background
max_iterations: 3
cost_threshold: medium
---
```

### Success/Failure Criteria

**Define clear criteria for each subagent task:**
- **Success criteria**: What constitutes successful completion
- **Failure criteria**: What constitutes failure requiring retry
- **Quality thresholds**: Minimum acceptable quality standards
- **Timeout limits**: Maximum execution time per subagent

### Decision Logic Implementation

**Orchestrator skills should:**
- Collect all subagent results
- Apply synthesis methodology
- Check evaluation gate criteria
- Implement iteration logic with limits
- Handle escalation to human review
- Document all decisions in audit trail

### Pattern Documentation

**Document reusable patterns for:**
- Common parallel execution scenarios
- Standard synthesis approaches
- Typical error recovery strategies
- Cost optimization techniques
- Governance enforcement integration

## Implementation Checklist

Before implementing subagent orchestration:

- [ ] Define clear parallel execution criteria
- [ ] Select appropriate subagent profiles
- [ ] Configure execution modes correctly
- [ ] Implement result synthesis logic
- [ ] Set up cost monitoring and thresholds
- [ ] Define iteration limits and escalation procedures
- [ ] Integrate with Overseer hooks for enforcement
- [ ] Configure state machine tracking
- [ ] Set up audit trail capture for all subagent activities
- [ ] Create orchestrator skills with proper frontmatter
- [ ] Document patterns and decision logic
- [ ] Test error recovery scenarios
- [ ] Validate cost management effectiveness
- [ ] Add comprehensive logging to all subagent implementations following standardized JSONL format
- [ ] Ensure subagent logging follows layer-specific log file conventions
- [ ] Include silent failure handling for all logging operations