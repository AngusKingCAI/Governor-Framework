# Universal Governor Rule Template
# Template: rule_name.yaml
# Use this as a template for both universal and agent-specific rules
# Replace placeholders with actual values, uncomment optional fields you use

id: rule_name
version: "1.0.0"
tier: warning  # OPTIONS: blocking, warning
# agent: architect  # OPTIONAL: for agent-specific rules (e.g., architect, executor, planner, researcher, reviewer)
name: rule_name
description: description
trigger:
  hook: SessionStart  # OPTIONS: SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop, PostCompaction
  # tool: exec  # OPTIONAL: for tool-specific rules (e.g., exec, edit, read)
  # tools: [exec, edit]  # OPTIONAL: for multiple tools (list format)
action: action_name  # The action name from Governor/actions/
params:
  reason: reason
  # allow_bypass: true  # OPTIONAL: Set to true to enable bypass menu for blocking rules
                      # USE CASES:
                      # - true: For optional blocking rules where user can override (e.g., workflow gates, testing blocks)
                      # - false/omit: For mandatory security rules where bypass should never be allowed (e.g., credential protection, critical security)
                      # FRAMEWORK BEHAVIOR: When allow_bypass=true, framework transforms deny decision to ask (bypass menu)
