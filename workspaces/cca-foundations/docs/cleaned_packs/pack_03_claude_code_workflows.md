# 📦 Pack 3: Claude Code Configuration & Workflows

> **Domain Coverage**: CCA-F Domain 3 (Claude Code Configuration & Workflows)  
> **Source Documents**: `anthropic_full_docs.md`, Claude Code Official Docs  
> **Target Concepts**: CLAUDE.md Hierarchy, Permission Model & Sandboxing, Headless/CI-CD Automation, Context Window Management

---

## 1. Claude Code Overview & Architecture

[Source: platform.claude.com/docs/en/agents-and-tools/claude-code/overview.md]

Claude Code is Anthropic's agentic coding assistant that runs in the terminal, IDE, and cloud environments. It operates in an iterative loop:
$$\text{Gather Context (Search/Read)} \longrightarrow \text{Take Action (Edit/Run Command)} \longrightarrow \text{Verify (Test/Lint)}$$

* **Key Native Capabilities**: Codebase-wide symbol search, intelligent file editing, bash command execution, git workflow management, and subagent orchestration.

---

## 2. `CLAUDE.md` Hierarchy & Rule Injection

[Source: platform.claude.com/docs/en/agents-and-tools/claude-code/configuration.md]

`CLAUDE.md` is the primary mechanism for injecting persistent context, architecture rules, and conventions into Claude Code.

### Resolution Hierarchy (from Highest to Lowest Priority):
1. **Subdirectory `CLAUDE.md`**: Applies to files within that specific directory and its children. Overrides parent rules.
2. **Project Root `CLAUDE.md`**: Shared across all contributors to the repository (committed to Git).
3. **User Global Config (`~/.claude/CLAUDE.md`)**: Personal developer preferences, global shortcuts, and personal tools across all projects.

### Best Practices for Authoring `CLAUDE.md`:
* **Concise & Imperative**: Use bullet points and sharp constraints rather than lengthy explanatory prose.
* **Include Build & Test Commands**: Explicitly provide common commands (e.g., `npm test`, `pytest`, `make check`).
* **Define Architecture & Boundaries**: Clearly state prohibited patterns (e.g., "Do not modify files outside `src/`", "Always use subtraction-first refactoring").

---

## 3. Permission Model & Sandbox Boundaries

[Source: platform.claude.com/docs/en/agents-and-tools/claude-code/security.md]

Claude Code provides granular permission control to balance developer speed with safety against unintentional system changes.

### Permission Levels:
* **Interactive Approval (Default)**: Claude requests explicit user confirmation before executing bash commands or modifying critical files.
* **Auto-Approved Tool Categories**:
  * Read-only operations (`FileRead`, `Grep`, `Glob`, `DirectoryList`) are typically auto-approved.
* **Execution Flags**:
  * `--dangerously-skip-permissions`: Disables interactive prompts. **Use strictly inside isolated containers or CI/CD pipelines.**
* **Sandbox Isolation**:
  * Running inside containerized or sandbox environments prevents runaway processes from affecting host machines or network environments.

---

## 4. Headless & CI/CD Automation Workflows

[Source: platform.claude.com/docs/en/agents-and-tools/claude-code/workflows.md]

Claude Code can run non-interactively (headless mode) for CI/CD checks, automated PR reviews, and scheduled refactoring tasks.

### Principles of Headless Operation:
* **Deterministic Verification Gates**: Every automated script MUST include automated verification steps (e.g., running `make check-all` or test suites) and exit with code 0 on success or non-zero on failure.
* **Atomic Pull Requests**: Output changes to an isolated feature branch and submit a GitHub Pull Request with a structured summary, rather than pushing directly to `main`.
* **Timeout & Cost Safeguards**: Enforce strict CI job timeouts and token spending limits to prevent unbounded budget consumption.

---

## 5. Context Window Management (`/compact`, `/clear`)

[Source: platform.claude.com/docs/en/agents-and-tools/claude-code/configuration.md]

Long-running coding sessions accumulate large token histories, leading to degraded reasoning and higher latency.

* **`/compact`**: Summarizes the ongoing conversation history, retaining key architectural decisions and current progress while dropping intermediate file read outputs.
* **`/clear`**: Completely resets the session memory while maintaining project-level `CLAUDE.md` context. Recommended between distinct, unrelated features.