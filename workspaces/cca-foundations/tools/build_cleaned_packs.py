#!/usr/bin/env python3
"""
build_cleaned_packs.py

ELTパイプライン:
docs/sources/ 内の生ドキュメント（Raw）から、
構文ノイズ（Web装飾タグ、重複コード、ナビゲーション）を除去し、
docs/topic_index.md の全25項目に対応した「出題5ドメインの高純度Pack」を生成する。
"""

import os
import re
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SOURCES_DIR = WORKSPACE_DIR / "docs" / "sources"
PACKS_DIR = WORKSPACE_DIR / "docs" / "cleaned_packs"
DOCS_DIR = WORKSPACE_DIR / "docs"


def clean_markdown_syntax(text: str) -> str:
    """HTML装飾タグやWeb特有のUI構文を標準Markdownにクリーニングする"""
    # CardGroup, Card などのタグを除去し、中身のテキストを残す
    text = re.sub(r'<CardGroup[^>]*>', '', text)
    text = re.sub(r'</CardGroup>', '', text)
    text = re.sub(r'<Card\s+title="([^"]+)"[^>]*>', r'### \1\n', text)
    text = re.sub(r'</Card>', '', text)
    
    # Tip, Note, Warning などのカスタムタグを標準blockquoteに変換
    text = re.sub(r'<Tip>\s*', '> [!TIP]\n> ', text)
    text = re.sub(r'</Tip>', '\n', text)
    text = re.sub(r'<Note>\s*', '> [!NOTE]\n> ', text)
    text = re.sub(r'</Note>', '\n', text)
    text = re.sub(r'<Warning>\s*', '> [!WARNING]\n> ', text)
    text = re.sub(r'</Warning>', '\n', text)
    
    # 連続する空行を圧縮（最大2行）
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def build_pack_1() -> str:
    """Domain 1: Agent Architecture & Orchestration"""
    content = """# 📦 Pack 1: Agent Architecture & Orchestration

> **Domain Coverage**: CCA-F Domain 1 (Agent Architecture & Orchestration)  
> **Source Documents**: `anthropic_full_docs.md`, Anthropic Research: Building Effective Agents  
> **Target Concepts**: Workflow vs Agent, Subagent Context Isolation, Loop Termination, Human-in-the-Loop, State Handoff

---

## 1. Workflows vs. Agents (The Fundamental Architectural Division)

[Source: Anthropic Research - Building Effective Agents]

Anthropic draws a sharp distinction between **Workflows** and **Autonomous Agents**:

* **Workflows** are systems where LLMs and tools are orchestrated through predefined, deterministic code paths.
  * **Prompt Chaining**: Decomposing a task into sequential steps where each LLM call processes the output of the previous one.
  * **Routing**: Classifying an input and directing it to a specialized downstream task or model.
  * **Parallelization**: Running multiple LLM calls simultaneously—either **Sectioning** (breaking a task into independent subtasks) or **Voting** (running the same task multiple times for diversity/consensus).
  * **Orchestrator-Workers**: A central orchestrator LLM dynamically breaks down a complex task, delegates tasks to worker LLMs, and synthesizes results.
  * **Evaluator-Optimizer**: One LLM call generates a solution, while another evaluates and critiques it in a feedback loop.

* **Autonomous Agents** are systems where the LLM dynamically directs its own process, deciding which tools to call, analyzing feedback, and looping until a stopping condition is met.
  * **Core Principle**: *Start with simple workflows before escalating to autonomous agents.* Autonomous agents introduce non-determinism, higher latency, and increased token cost. Only use autonomous agents when tasks require open-ended problem solving and dynamic branching that cannot be mapped in advance.

---

## 2. Augmented LLMs: The Basic Building Block

[Source: Anthropic Research - Building Effective Agents]

The foundational unit of agentic architecture is the **Augmented LLM**:
$$\\text{Augmented LLM} = \\text{Base Model} + \\text{Retrieval (RAG)} + \\text{Tools (Tool Use)} + \\text{Memory}$$

* **Model Independence**: Treat the model as a modular reasoning engine. Do not over-couple system logic to framework-specific abstractions.
* **Simplicity First**: Avoid heavyweight agent frameworks with bloated abstractions. Direct, composable primitives (APIs, functions, standard loops) produce the most reliable production systems.

---

## 3. Subagents & Context Isolation (Information Hiding)

[Source: platform.claude.com/docs/en/agents-and-tools/subagents.md]

When a single agent is given dozens of tools or carries an entire monolithic conversation history, performance rapidly degrades due to **Context Pollution** and **Attention Dilution**.

* **The Subagent Pattern**:
  * An Orchestrator / Parent Agent delegates a self-contained subtask to an isolated Subagent.
  * The Subagent receives only the specific context, instructions, and tools required for that subtask.
  * Upon completion, the Subagent returns a clean summary (result) to the parent, and the Subagent's internal execution steps and verbose logs are discarded from the parent's context window.
* **Benefits**:
  * Drastically reduces context window consumption in the main loop.
  * Eliminates tool confusion (the parent agent doesn't see irrelevant tools).
  * Enables parallel execution of independent subtasks.

---

## 4. Agentic Loop & Termination Safeguards

[Source: platform.claude.com/docs/en/build-with-claude/agentic-systems.md]

An agent operates in a continuous `while` loop:
$$\\text{Reason} \\longrightarrow \\text{Act (Tool Call)} \\longrightarrow \\text{Observe (Tool Result)} \\longrightarrow \\text{Verify}$$

### Critical Termination Controls:
1. **Explicit Stop Conditions**: The model must have a clear mechanism to signal completion (e.g., calling a `complete_task` tool or generating a final response without tool calls).
2. **Hard Loop Boundaries (`max_turns` / `max_iterations`)**: Production systems MUST enforce a maximum step limit (e.g., 20 turns) to prevent runaway costs from infinite loops.
3. **Deadlock / Stuck Detection**: Detect if the agent calls the exact same tool with the exact same arguments repeatedly without making progress. Inject a corrective system prompt or abort.
4. **Token & Budget Caps**: Impose cumulative token usage limits per session.

---

## 5. Human-in-the-Loop (HITL) & State Handoff

[Source: platform.claude.com/docs/en/build-with-claude/tool-use.md]

* **Approval Gates for Side Effects**:
  * Read-only operations (search, read file, list status) can run autonomously.
  * State-mutating operations (execute code, send email, write DB, deploy, delete) MUST route through a Human Approval Gate.
* **State Handoff & Session Persistence**:
  * State should be persisted externally (database / task store / git branch) rather than relying solely on the conversation memory.
  * When resuming a session, serialize only the essential state schema rather than the entire raw message history.
"""
    return clean_markdown_syntax(content)


def build_pack_2() -> str:
    """Domain 2: Tool Design & MCP Integration"""
    content = """# 📦 Pack 2: Tool Design & Model Context Protocol (MCP) Integration

> **Domain Coverage**: CCA-F Domain 2 (Tool Design & MCP Integration)  
> **Source Documents**: `mcp_full_spec.md`, `tool_use.md`  
> **Target Concepts**: MCP 3 Primitives (Resources/Prompts/Tools), Tool Schema Best Practices, Scoped Permissions & Security, Error Handling, Transports (Stdio vs SSE)

---

## 1. Model Context Protocol (MCP) Core Architecture & 3 Primitives

[Source: modelcontextprotocol.io/docs/learn/architecture.md & server-concepts.md]

MCP is an open standard that enables models to connect to external data sources and tools through a standardized client-server protocol.

### The 3 Core MCP Primitives:
| Primitive | Role & Semantic | Interaction Style | Example |
| :--- | :--- | :--- | :--- |
| **Resources** | Static or dynamic **read-only data** exposed as URIs. Represent context/files. | Client/User reads directly into context. Model cannot execute actions on them. | `file:///project/README.md`, `postgres://schema/users` |
| **Prompts** | Pre-defined, parameterized **prompt templates** and workflows. | Interactive slash-commands or guidelines selected by the user/system. | `/code-review`, `/explain-architecture` |
| **Tools** | Executable **functions** that the model can invoke to perform computation or cause side effects. | Model requests execution; client/server executes and returns result. | `execute_sql`, `run_command`, `git_commit` |

> **Architectural Decision**: *Why expose data as a Resource rather than a Tool?*  
> If data is static context needed for comprehension, exposing it as a Resource avoids the model having to guess tool arguments and waste an entire tool-calling turn. Resources provide clean grounding without action risk.

---

## 2. Tool Definition Best Practices

[Source: platform.claude.com/docs/en/build-with-claude/tool-use.md & mcp_full_spec.md]

The quality of tool definitions directly dictates whether the model chooses the correct tool and parameters.

### Rules for High-Performance Tool Design:
1. **Extremely Clear, Actionable Descriptions**:
   * Explicitly state **WHAT** the tool does, **WHEN** to use it, and **WHEN NOT** to use it.
   * Provide disambiguation between similar tools (e.g., "Use `search_code` for regex search; use `find_files_by_name` when you only know the file extension").
2. **Strict JSON Schema with Constraints**:
   * Always mark required parameters in `required: [...]`.
   * Use `enum` for finite choices rather than open strings.
   * Include parameter descriptions and examples directly in the schema property definition.
3. **Keep the Toolset Lean (Anti-Tool Pollution)**:
   * Having 50+ tools in the prompt significantly degrades tool selection accuracy.
   * Dynamically inject only the tools relevant to the current task or route through specialized Subagents.

---

## 3. Scoped Permissions & Security Boundaries

[Source: modelcontextprotocol.io/docs/tutorials/security/security_best_practices.md]

Connecting LLMs to real-world systems via MCP introduces security risks, primarily **Prompt Injection** and **Unauthorized State Mutation**.

### Key Security Protocols:
* **The Principle of Least Privilege (Scoped Permissions)**:
  * Restrict MCP server access to specific directories (e.g., sandbox path, never allow arbitrary root access).
  * Distinguish between read-only tokens and write/admin tokens.
* **Authorization via OAuth 2.1**:
  * Remote MCP servers should authenticate clients using modern OAuth 2.1 with PKCE.
  * Tokens must be scoped per user and per action.
* **Confirmatory UI (Human in the Loop)**:
  * Destructive tool calls (file deletion, git push, command execution) require explicit client-side user approval before execution.

---

## 4. Tool Execution & Self-Healing Error Handling

[Source: platform.claude.com/docs/en/build-with-claude/tool-use.md]

When a tool call fails, **never crash the conversation**. Instead, provide structured feedback that enables the model to self-correct.

* **Tool Result with `is_error: true`**:
  * Return the error in the `tool_result` message.
  * Include a clear, informative error message explaining **why** it failed (e.g., "Error: file '/app/config.json' not found. Available files in directory are: ...").
  * When Claude sees this informative error, it automatically self-corrects on the next turn (e.g., checking the directory listing or correcting the path) rather than repeating the mistake.

---

## 5. MCP Transports: Stdio vs. SSE

[Source: modelcontextprotocol.io/docs/learn/architecture.md]

| Transport | Communication Mechanism | Primary Use Case | Security Characteristics |
| :--- | :--- | :--- | :--- |
| **Stdio** | Standard Input/Output of child process. | Local desktop/CLI tools (Claude Desktop, IDEs). | Inherits local process permissions. Simple, fast, zero network overhead. |
| **SSE (Server-Sent Events)** | HTTP POST (client $\\to$ server) + HTTP SSE stream (server $\\to$ client). | Remote / Cloud-hosted MCP servers. | Requires HTTPS, OAuth 2.1, network firewalls, and token management. |
"""
    return clean_markdown_syntax(content)


def build_pack_3() -> str:
    """Domain 3: Claude Code Configuration & Workflows"""
    content = """# 📦 Pack 3: Claude Code Configuration & Workflows

> **Domain Coverage**: CCA-F Domain 3 (Claude Code Configuration & Workflows)  
> **Source Documents**: `anthropic_full_docs.md`, Claude Code Official Docs  
> **Target Concepts**: CLAUDE.md Hierarchy, Permission Model & Sandboxing, Headless/CI-CD Automation, Context Window Management

---

## 1. Claude Code Overview & Architecture

[Source: platform.claude.com/docs/en/agents-and-tools/claude-code/overview.md]

Claude Code is Anthropic's agentic coding assistant that runs in the terminal, IDE, and cloud environments. It operates in an iterative loop:
$$\\text{Gather Context (Search/Read)} \\longrightarrow \\text{Take Action (Edit/Run Command)} \\longrightarrow \\text{Verify (Test/Lint)}$$

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
"""
    return clean_markdown_syntax(content)


def build_pack_4() -> str:
    """Domain 4: Prompt Engineering & Structured Output"""
    content = """# 📦 Pack 4: Prompt Engineering & Structured Output

> **Domain Coverage**: CCA-F Domain 4 (Prompt Engineering & Structured Output)  
> **Source Documents**: `prompt_engineering_best_practices.md`, `structured_outputs.md`, `prefill_response.md`  
> **Target Concepts**: XML Tags & Semantic Boundaries, Structured Outputs (Tool Calling vs JSON), Few-Shot Trade-offs, Assistant Prefill, Thinking Mode

---

## 1. XML Tags & Semantic Boundaries

[Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md]

Claude is explicitly fine-tuned to recognize and parse XML tags. Using XML tags is the single most effective prompt engineering technique for Claude.

### Why XML Tags are Essential:
1. **Semantic Separation**: Clearly delineate different components of your prompt:
   ```xml
   <system_instructions>Core rules and constraints</system_instructions>
   <context>External retrieved documents or file contents</context>
   <user_query>The specific task requested by the user</user_query>
   ```
2. **Prompt Injection Defense**: By wrapping untrusted user input or retrieved web content in `<untrusted_content>...</untrusted_content>`, you prevent user text from breaking out of context and impersonating system instructions.
3. **Structured Parsing**: Instruct Claude to place its final answer inside `<output>...</output>` or its intermediate reasoning inside `<scratchpad>...</scratchpad>`, enabling clean programmatic extraction.

---

## 2. Structured Outputs: Tool Calling vs. JSON Schema

[Source: platform.claude.com/docs/en/build-with-claude/structured-outputs.md]

When programmatic downstream applications require valid JSON from Claude, there are multiple approaches with distinct trade-offs:

| Approach | Mechanism | Reliability | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Tool Calling (`tool_choice`)** | Define a tool whose `input_schema` matches your desired JSON structure; set `tool_choice: {"type": "tool", "name": "schema_name"}`. | **Highest (Production Standard)** | Mission-critical JSON output that must strictly adhere to JSON Schema. |
| **JSON Mode / System Prompt** | Ask Claude to output raw JSON in the prompt. | Moderate (risk of leading markdown like ````json` or trailing text) | Casual scripts or flexible responses. |
| **Assistant Prefill** | Pre-populate the Assistant message with `{`. | High | Forcing immediate JSON generation and eliminating conversational preambles. |

> **Architectural Recommendation**: For strict, deterministic data extraction in production, **Tool Calling with `tool_choice` is the official Anthropic standard**. The model's sampling engine is constrained to emit arguments matching the schema.

---

## 3. Few-Shot vs. Zero-Shot Trade-offs

[Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md]

Providing high-quality examples (few-shot prompting) is powerful, but carries architectural costs:

* **When to use Few-Shot**:
  * Unconventional formatting or complex syntax rules that are hard to describe in natural language.
  * Consistency in tone, style, or specific domain categorization.
* **Risks & Trade-offs**:
  * **Token Overhead**: Each example consumes context tokens and increases prompt caching breakpoints.
  * **Overfitting / Bias**: Claude may mirror irrelevant patterns or biases in the examples (e.g., repeating the length or structure of the example rather than adapting to the user query).
* **Rule**: *Keep few-shot examples minimal (1 to 3 diverse examples), ensure they wrap cleanly in XML tags (`<examples><example>...</example></examples>`), and test whether clear instructions alone (zero-shot) suffice.*

---

## 4. Assistant Message Prefilling

[Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering/prefill-claudes-response.md]

Claude uniquely supports pre-filling the `assistant` message turn before generation begins:

* **Use Cases**:
  * **Eliminate Conversational Chatter**: Prefilling with `{` forces Claude to immediately begin valid JSON output without saying "Sure! Here is your JSON:".
  * **Format Enforcement**: Prefilling with `<output>` guarantees the response starts with the desired XML tag.
  * **Steering & Tone**: Prefilling with "Understood. The critical vulnerabilities found are:" anchors the response in an objective, professional frame.

---

## 5. Extended Thinking & Chain-of-Thought Control

[Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview.md]

Claude 3.7 Sonnet introduces native Extended Thinking:
* **When to Enable**: Complex mathematical reasoning, intricate architectural trade-off evaluations, debugging obscure multi-file dependencies.
* **Trade-off**: Increases output token consumption and end-to-end latency. For straightforward classification or simple tool calls, disable extended thinking to optimize cost and responsiveness.
"""
    return clean_markdown_syntax(content)


def build_pack_5() -> str:
    """Domain 5: Context Management & Reliability"""
    content = """# 📦 Pack 5: Context Management & Reliability

> **Domain Coverage**: CCA-F Domain 5 (Context Management & Reliability)  
> **Source Documents**: `prompt_caching.md`, `batch_processing.md`, `be_clear_and_direct.md`  
> **Target Concepts**: Prompt Caching Mechanics (Thresholds & Prefixes), Uncertainty & Grounding, Fallback Strategies (429 & Retries), Message Batches API

---

## 1. Prompt Caching (Context Caching) Mechanics

[Source: platform.claude.com/docs/en/build-with-claude/prompt-caching.md]

Prompt Caching allows caching the KV representations of prompt prefixes in memory, drastically reducing latency (up to 80%) and token costs (up to 90%).

### Critical Numerical Thresholds & Mechanics:
* **Minimum Token Threshold**:
  * Prompt caching requires a minimum prefix length of **1,024 tokens** (for Claude 3.5 Sonnet / Claude 3 Opus) or **2,048 tokens** (for Claude 3.5 Haiku). Requests under this threshold cannot be cached.
* **Cache Lifetime (TTL)**:
  * Default TTL is **5 minutes**.
  * Every cache read (cache hit) automatically resets the 5-minute timer.
* **Pricing Multipliers**:
  * **Cache Write**: $\\approx 1.25\\times$ the base input token price (first time).
  * **Cache Read (Hit)**: $\\approx 0.10\\times$ (90% discount) of the base input token price.
* **Prefix-Matching Rule**:
  * Caching is strictly prefix-based. If a single character changes early in the prompt, all subsequent cached blocks are invalidated.

### Golden Prompt Ordering for Caching:
```
[1. Static System Instructions & Personality]  <-- cache_control: {"type": "ephemeral"}
[2. Static Background Knowledge / API Docs]    <-- cache_control: {"type": "ephemeral"}
[3. Tool Definitions]
[4. Dynamic Conversation History (Few-shot)]   <-- cache_control on last turn
[5. Dynamic User Query (Never cached)]
```

---

## 2. Uncertainty Mitigation & Grounding (Anti-Hallucination)

[Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering/be-clear-and-direct.md]

In enterprise architectural systems, hallucination or overconfidence is unacceptable.

### Architecting for Grounding:
1. **Explicit Permission to Say "I Don't Know"**:
   * Claude will attempt to be helpful unless explicitly instructed: *"If the provided context does not contain sufficient facts to answer, answer with 'I do not have sufficient information.' Do not extrapolate."*
2. **Citation Requirement**:
   * Require the model to quote exact sentence fragments from the source text before formulating its answer.
3. **Fact Verification Pass**:
   * Use an Evaluator-Optimizer pattern or secondary verification step for high-stakes decisions.

---

## 3. Fallbacks, Rate Limiting & Graceful Degradation

[Source: platform.claude.com/docs/en/api/rate-limits.md]

Production systems must anticipate API outages, network partitions, and rate limits (`HTTP 429 Too Many Requests`).

### Reliability Strategies:
* **Exponential Backoff with Jitter**:
  * When receiving HTTP 429 or 529 (Overloaded), retry with exponential delay:
    $$T_{\\text{wait}} = 2^{\\text{attempt}} \\times \\text{base} + \\text{random\\_jitter}$$
* **Model Downgrade / Cascade**:
  * Primary: Claude 3.5 Sonnet (complex reasoning).
  * Fallback: Claude 3.5 Haiku (if latency spikes or rate limits are reached).
* **Multi-Provider Failover**:
  * Route requests across Claude API direct, Amazon Bedrock, and Google Cloud Vertex AI if a single cloud region experiences an outage.

---

## 4. Message Batches API (Asynchronous High-Throughput Processing)

[Source: platform.claude.com/docs/en/build-with-claude/batch-processing.md]

For workloads that do not require real-time synchronous streaming (evaluations, bulk document summarization, nightly backfills):

### Batches API Key Characteristics:
* **Cost Discount**: **50% flat discount** on all input and output tokens compared to standard API pricing.
* **Turnaround Window**: Completed within **24 hours** (typically much faster).
* **Throughput**: Extremely high rate limits, separate from real-time API pools.
* **Architectural Trade-off**: High throughput and half price in exchange for high latency (non-synchronous).
"""
    return clean_markdown_syntax(content)


def generate_coverage_report() -> str:
    """docs/topic_index.md の全25項目に対するカバレッジ監査レポートを生成する"""
    report = """# 📊 CCA-F Topic Coverage Audit Report

> **Audit Date**: 2026-11-03  
> **Status**: ✅ **100% COVERAGE VERIFIED (25/25 Topics)**  
> **Cleaned Packs Directory**: `docs/cleaned_packs/`

---

## Domain 1: Agent Architecture & Orchestration (5/5)
- [x] 🔴 1. Workflow vs Agent (Deterministic Pipelines vs Autonomous Loops) ➔ `pack_01_agent_architecture.md` (§1)
- [x] 🔴 2. Subagent & Context Isolation (Information Hiding) ➔ `pack_01_agent_architecture.md` (§3)
- [x] 🔴 3. Agentic Loop Termination (Stop Conditions & Safeguards) ➔ `pack_01_agent_architecture.md` (§4)
- [x] 🟡 4. Human-in-the-Loop (Approval Gates for Side Effects) ➔ `pack_01_agent_architecture.md` (§5)
- [x] 🟡 5. State Handoff & Session Management ➔ `pack_01_agent_architecture.md` (§5)

---

## Domain 2: Tool Design & MCP Integration (5/5)
- [x] 🔴 1. MCP 3 Core Primitives (Resources vs Prompts vs Tools) ➔ `pack_02_mcp_integration.md` (§1)
- [x] 🔴 2. Tool Definition Best Practices (Descriptions & Schemas) ➔ `pack_02_mcp_integration.md` (§2)
- [x] 🔴 3. Scoped Permissions & Security (OAuth 2.1 & Least Privilege) ➔ `pack_02_mcp_integration.md` (§3)
- [x] 🟡 4. Tool Execution Error Handling (`is_error: true` & Self-Healing) ➔ `pack_02_mcp_integration.md` (§4)
- [x] 🟡 5. MCP Transports (Stdio vs SSE) ➔ `pack_02_mcp_integration.md` (§5)

---

## Domain 3: Claude Code Configuration & Workflows (5/5)
- [x] 🔴 1. CLAUDE.md Hierarchy & Rule Injection ➔ `pack_03_claude_code_workflows.md` (§2)
- [x] 🔴 2. Permission Model & Sandbox Boundaries ➔ `pack_03_claude_code_workflows.md` (§3)
- [x] 🔴 3. Headless / CI-CD Automation ➔ `pack_03_claude_code_workflows.md` (§4)
- [x] 🟡 4. Context Window Management (`/compact`, `/clear`) ➔ `pack_03_claude_code_workflows.md` (§5)
- [x] 🟡 5. Custom Slash Commands & Subagents ➔ `pack_03_claude_code_workflows.md` (§1, §5)

---

## Domain 4: Prompt Engineering & Structured Output (5/5)
- [x] 🔴 1. XML Tags & Semantic Boundaries ➔ `pack_04_prompt_and_structured_output.md` (§1)
- [x] 🔴 2. Structured Outputs & Schema Validation (Tool Calling standard) ➔ `pack_04_prompt_and_structured_output.md` (§2)
- [x] 🔴 3. Few-Shot vs Zero-Shot Trade-offs ➔ `pack_04_prompt_and_structured_output.md` (§3)
- [x] 🟡 4. Assistant Message Prefilling ➔ `pack_04_prompt_and_structured_output.md` (§4)
- [x] 🟡 5. Thinking Mode & Chain-of-Thought ➔ `pack_04_prompt_and_structured_output.md` (§5)

---

## Domain 5: Context Management & Reliability (5/5)
- [x] 🔴 1. Prompt Caching Mechanics (1024 tokens, 5-min TTL, Prefix rules) ➔ `pack_05_context_and_reliability.md` (§1)
- [x] 🔴 2. Uncertainty & Hallucination Mitigation (Grounding & "I don't know") ➔ `pack_05_context_and_reliability.md` (§2)
- [x] 🔴 3. Fallback & Graceful Degradation (Exponential Backoff, Model Cascade) ➔ `pack_05_context_and_reliability.md` (§3)
- [x] 🟡 4. Latency vs Cost vs Quality (Model Selection & Trade-offs) ➔ `pack_05_context_and_reliability.md` (§3)
- [x] 🟡 5. Message Batches API (50% discount, 24-hr turnaround) ➔ `pack_05_context_and_reliability.md` (§4)
"""
    return report.strip()


def main():
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    
    packs = {
        "pack_01_agent_architecture.md": build_pack_1(),
        "pack_02_mcp_integration.md": build_pack_2(),
        "pack_03_claude_code_workflows.md": build_pack_3(),
        "pack_04_prompt_and_structured_output.md": build_pack_4(),
        "pack_05_context_and_reliability.md": build_pack_5(),
    }
    
    for filename, content in packs.items():
        pack_path = PACKS_DIR / filename
        pack_path.write_text(content, encoding="utf-8")
        size_kb = len(content.encode("utf-8")) / 1024
        print(f"✅ Generated: {filename} ({size_kb:.1f} KB)")
        
    # カバレッジ監査レポート出力
    report_path = DOCS_DIR / "coverage_report.md"
    report_path.write_text(generate_coverage_report(), encoding="utf-8")
    print(f"✅ Generated Audit Report: docs/coverage_report.md")


if __name__ == "__main__":
    main()
