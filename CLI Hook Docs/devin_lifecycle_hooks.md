# Devin CLI Lifecycle Hooks Documentation

Source: https://docs.devin.ai/cli/extensibility/hooks/lifecycle-hooks

## Overview

Each hook event fires at a specific point in the agent's lifecycle. Use the **matcher** field (a regex matched against the hook event's `tool_name`) to filter which tool invocations trigger your hook.

In addition to the event-specific fields below, every stdin payload includes a stable per-session `session_id` and a per-turn `prompt_id` (rotated on every user prompt; absent for events that fire before the first user prompt, e.g. `SessionStart`).

## Hook Events

### PreToolUse

Fires **before** a tool executes. Use this to block, modify, or add context to tool calls.

**Stdin data:**

| Field        | Description                   | Example                                         |
| ------------ | ----------------------------- | ----------------------------------------------- |
| `tool_name`  | Name of the tool being called | `exec`, `edit`, `mcp__github__create_issue`     |
| `tool_input` | Arguments passed to the tool  | `{ "command": "rm -rf /", "shell_id": "main" }` |

**Example — Block destructive commands:**

```json
{
  "PreToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "python3 -c \"import sys, json; data = json.load(sys.stdin); cmd = data.get('tool_input', {}).get('command', ''); sys.exit(2 if 'rm -rf' in cmd else 0)\""
        }
      ]
    }
  ]
}
```

**Example — Rewrite commands before execution:**

A hook can transparently rewrite the tool's input by printing `hookSpecificOutput.updatedInput` to stdout:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": {
      "command": "rtk git status"
    }
  }
}
```

### PostToolUse

Fires **after** a tool finishes executing. Use this for logging, validation, or triggering follow-up actions.

**Stdin data:**

| Field           | Description                                                                      |
| --------------- | -------------------------------------------------------------------------------- |
| `tool_name`     | Name of the tool that ran                                                        |
| `tool_input`    | Arguments that were passed                                                       |
| `tool_response` | Object with `success` (boolean), `output` (string), and `error` (string or null) |

**Example — Log all shell commands:**

```json
{
  "PostToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "sh -c 'cat >> ~/.devin-command-log'"
        }
      ]
    }
  ]
}
```

### PermissionRequest

Fires when the agent needs a permission decision. Use this to implement custom approval logic.

**Stdin data:**

| Field        | Description                 |
| ------------ | --------------------------- |
| `tool_name`  | Tool requesting permission  |
| `tool_input` | Arguments for the tool call |

**Example — Auto-approve git commands:**

```json
{
  "PermissionRequest": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "python3 -c \"import sys, json; data = json.load(sys.stdin); cmd = data.get('tool_input', {}).get('command', ''); print(json.dumps({'decision': 'approve'})) if cmd.startswith('git ') else sys.exit(0)\""
        }
      ]
    }
  ]
}
```

### UserPromptSubmit

Fires when the user submits a message. Use this to add context or trigger workflows.

**Stdin data:**

| Field    | Description             |
| -------- | ----------------------- |
| `prompt` | The user's message text |

**Example — Inject context on every prompt:**

```json
{
  "UserPromptSubmit": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"UserPromptSubmit\", \"additionalContext\": \"Deploys require an approved change ticket.\"}}'"
        }
      ]
    }
  ]
}
```

### Stop

Fires when the agent decides to stop (finish its turn). Use this to add follow-up instructions or prevent premature stopping.

**Stdin data:**

| Field              | Description                           |
| ------------------ | ------------------------------------- |
| `stop_hook_active` | Whether a stop hook is already active |

**Example — Remind agent to run tests:**

```json
{
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "echo '{\"decision\": \"block\", \"reason\": \"Please run the test suite before stopping.\"}'"
        }
      ]
    }
  ]
}
```

### PostCompaction

Fires **after** context compaction completes successfully. Use this for logging, triggering follow-up actions, or re-injecting context that may have been lost during compaction.

**Stdin data:**

| Field     | Description                                                                      |
| --------- | -------------------------------------------------------------------------------- |
| `summary` | Summary text produced by the compactor (may be null if no summary was generated) |

### SessionStart

Fires when a new session begins. Use this for initialization, logging, or environment setup.

**Stdin data:**

| Field    | Description                 |
| -------- | --------------------------- |
| `source` | How the session was started |

**Example — Run setup script:**

```json
{
  "SessionStart": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "./scripts/dev-setup.sh",
          "timeout": 10
        }
      ]
    }
  ]
}
```

### SessionEnd

Fires when a session ends. Use this for cleanup or final logging.

**Stdin data:**

| Field    | Description           |
| -------- | --------------------- |
| `reason` | Why the session ended |

## Using the Matcher

The `matcher` field is a **regex** matched against the hook event's `tool_name`. It is available for tool-related events: `PreToolUse`, `PostToolUse`, and `PermissionRequest`.

For non-tool events (`UserPromptSubmit`, `Stop`, `PostCompaction`, `SessionStart`, and `SessionEnd`), there is no `tool_name`; use `""` or omit the matcher to run the hook for every event of that type.

| Matcher                         | Matches                                              |
| ------------------------------- | ---------------------------------------------------- |
| `""` (empty) or omitted         | All tool names for tool events                       |
| `"exec"`                        | Tool names containing `exec`                         |
| `"^exec$"`                      | Only the `exec` tool                                 |
| `"^(exec\|edit)$"`              | Only `exec` or `edit`                                |
| `"^mcp__.*"`                    | All MCP tools                                        |
| `"^mcp__github__.*"`            | All tools from the `github` MCP server               |
| `"^mcp__github__create_issue$"` | The `create_issue` tool from the `github` MCP server |

## Hook Format

Each hook has a **type** (`command` or `prompt`), an optional **matcher** (regex on the hook event's `tool_name`), and configuration:

| Field      | Description |
| ---------- | -------------------------------------------------------------- |
| `matcher`  | Regex matched against the hook event's `tool_name`           |
| `type`     | Either `command` (for hooks that run external commands) or `prompt` (for hooks that run LLM prompts) |
| `command`  | The external command to run (for `command` type hooks)       |
| `timeout`  | Optional timeout in seconds (for `command` type hooks)        |
