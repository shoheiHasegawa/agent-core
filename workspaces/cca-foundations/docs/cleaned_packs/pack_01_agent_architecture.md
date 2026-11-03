# 📦 Pack 1: Agent Architecture & Orchestration

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
$$\text{Augmented LLM} = \text{Base Model} + \text{Retrieval (RAG)} + \text{Tools (Tool Use)} + \text{Memory}$$

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
$$\text{Reason} \longrightarrow \text{Act (Tool Call)} \longrightarrow \text{Observe (Tool Result)} \longrightarrow \text{Verify}$$

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