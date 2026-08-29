# Harness Engineering Investigation: Must-Level Debts in Agentic OS

## 1. Executive Summary
From a Harness Engineering perspective, the current Agentic OS heavily relies on **"Prompt-based Soft Constraints"** (defined in `GEMINI.md` and `AGENT.md`) rather than **"System-level Hard Constraints"**. This is a MUST-level technical debt because LLM non-determinism guarantees that these rules will eventually be violated, leading to potential system degradation, broken Single Source of Truth (SSOT), and unsafe executions.

## 2. Identified MUST-Level Debts

### 2.1. Lack of Tool-Level Interceptors (Gatekeepers)
- **Current State**: `AGENT.md` instructs agents to pass "Quality Gates" (`make check-all`) and undergo double reviews (`global-alignment-reviewer` and `compliance-reviewer`) before making core modifications.
- **Problem**: These are merely prompt instructions to the LLM. There is no architectural interceptor blocking the `replace_file_content` or `run_command` tools if the gates are not passed. The agent can simply ignore the reviewer steps.
- **Harness Solution (Hard Constraint)**: Introduce an Interceptor/Middleware in the tool execution pipeline. For example, modifying a core file should natively require an authorization token generated only after `make check-all` succeeds, or tool calls modifying core files should automatically trigger the reviewer subagents before persisting the changes.

### 2.2. Over-reliance on Generic CLI vs Native Tools
- **Current State**: The system relies on shell commands (`run_command`) and generic edits, expecting the agent to self-regulate (e.g., "commit before destructive actions", "set -e").
- **Problem**: Generic CLI tools give the agent unbound access. The OS lacks specialized, constrained Native Tools (e.g., MCP servers) for safe operations. Expecting an LLM to string together bash commands reliably for complex workflows is fragile.
- **Harness Solution (Hard Constraint)**: Restrict generic CLI access. Provide Native Tools for critical workflows (e.g., a state-machine-driven task completer tool that automatically runs tests and reviewers, rather than expecting the agent to manually orchestrate them via CLI).

### 2.3. Execution Environment Weaknesses & Lack of Sandboxing
- **Current State**: `GEMINI.md` states "Leave No Trace", dictates using `agent-core/scratch/` for temp files, and prohibits writing API keys to code.
- **Problem**: The execution environment does not physically restrict the agent. It can theoretically write anywhere, pollute the workspace, or echo secrets to logs.
- **Harness Solution (Hard Constraint)**: Implement a true execution sandbox (e.g., restricted directory mounts, env var isolation). Use native file-system APIs that throw permission errors if the agent attempts to write outside designated workspaces.

### 2.4. Missing Test Harnesses for Agent Behavior
- **Current State**: We have `make check-all` for static code, but no harness to verify the Agent's behavioral adherence to OS rules.
- **Problem**: We cannot deterministically prove that the Agent respects the `global-alignment-reviewer` protocol because we don't have an Agentic Test Harness.
- **Harness Solution (Hard Constraint)**: Build a simulation test harness that mocks user requests and asserts that the agent reliably invokes the required reviewer skills and test commands before completion.

## 3. Action Plan (Next Steps)
1. **Design an Interceptor Middleware**: Intercept `write_to_file` and `replace_file_content` calls targeting core directories to enforce SSOT updates and tests natively.
2. **Migrate to Native Tools**: Replace prompt-based quality gates with dedicated tools (e.g., `handoff_task` tool that runs all checks internally).
3. **Environment Sandboxing**: Enforce directory sandboxing at the tool/environment level, stripping away relying on prompt-based `WHERE` boundaries.
