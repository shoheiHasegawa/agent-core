# Prompt Engineering Investigation Report: You_Inc Agentic OS

## Overview
Based on a Prompt Engineering perspective, the current system prompts (`GEMINI.md`, various `AGENT.md` files, and `agent-core/docs/`) rely heavily on complex, philosophical guidelines and "soft constraints" (asking the LLM nicely) rather than deterministic workflows, specific tool schemas, or system-level constraints. This approach increases cognitive load, consumes context windows unnecessarily, and leads to inconsistent agent behavior.

## MUST-Level Debts Identified

### 1. Over-reliance on "Soft Constraints" for Critical Workflows
**Issue**: Critical system state updates and quality gates are enforced via markdown instructions ("asking nicely") rather than deterministic tooling.
- **Evidence**: `agent-core/AGENT.md` instructs the agent to manually update `progress.md`/`task.md` to prevent "amnesia" and manually ensure `make check-all` passes before ending a session. `GEMINI.md` mandates "Atomic Update" of docs alongside code.
- **Why it's a debt**: LLMs suffer from "lost in the middle" syndrome and context drift. They will inevitably forget to update `progress.md` or run tests before exiting if it's just a text instruction. 
- **Resolution**: Convert these into deterministic tool constraints. For example, replacing a generic CLI tool with a `handoff_task` tool that automatically runs the test suite and blocks completion if tests fail. Use a specific `update_progress` tool that tracks state, rather than relying on manual file edits.

### 2. Contradictory Instructions (Hesitation vs. Autonomy)
**Issue**: The prompts give conflicting directives regarding agent autonomy, which will cause the LLM to enter a "hesitation loop" (constantly asking for permission) or hallucinate to bypass restrictions.
- **Evidence**: 
  - `GEMINI.md` explicitly forbids "Zero-Shot Execution" (unconfirmed execution) and demands proposals for any change, but simultaneously instructs the agent to act as a "strategic staff" and explore "What if" scenarios for edge cases.
  - `core-service/AGENT.md` forbids running tests directly ("自己判断でテストを叩かず"), forcing the agent through a theoretical `verify_loop_state.py` gate, but also demands strict "Double-loop TDD".
- **Why it's a debt**: The LLM cannot reliably balance "always ask first" with "be autonomous and explore". This degrades performance, as the LLM will likely pause for user input on trivial tasks, or ignore the rule entirely.
- **Resolution**: Clarify the boundaries programmatically. If proposals are required, provide a `submit_proposal` tool that halts execution until user approval. Remove abstract contradictions.

### 3. High Cognitive Load and Prompt Bloat
**Issue**: The `AGENT.md` files and `GEMINI.md` mix routing (`<jit_routing>`), abstract philosophy (`<philosophy_and_tradeoff>`), and execution rules (`<governance>`) in the same context window.
- **Evidence**: `agent-core/AGENT.md` requires the agent to remember to formulate "Plan A, Plan B, and Do Nothing" for escalations, evaluate "Two-Way Door" reversibility, and triage issues into 3 complex levels (`GEMINI.md`).
- **Why it's a debt**: Complex reasoning frameworks (like generating 3 options and evaluating reversibility) embedded as background rules dilute the primary task focus. LLMs perform poorly when burdened with too many background meta-tasks.
- **Resolution**: Separate concerns. Routing and dynamic loading (JIT) should be handled by the MCP/Tool layer or standard RAG, not manual markdown pointers. Complex frameworks like "Plan A/Plan B" should only be injected into the prompt *when* an escalation tool is invoked, not kept in the global context.

### 4. Over-complication of Knowledge Distillation
**Issue**: The rules for the `second-brain` workspace demand an unreasonably high level of cognitive abstraction for every single task.
- **Evidence**: `second-brain/AGENT.md` demands that agents do not just summarize, but *must* append "falsifications (反証)" or "analogies (アナロジー)" to every note.
- **Why it's a debt**: Forcing a specific dialectic framework onto every interaction with the knowledge base is prompt-heavy and will lead to forced, low-quality hallucinations just to satisfy the constraint.
- **Resolution**: Relax the absolute constraints. Create specialized sub-agents or specific tools (e.g., `distill_knowledge_with_analogy`) that are invoked only when appropriate, rather than making it a global mandate for the directory.

## Summary Recommendation
Shift from **"Instruction-Driven Governance"** (writing more rules in Markdown) to **"Tool-Driven Governance"** (exposing narrow, state-validating tools). Strip abstract philosophies from the system prompts and replace them with explicit tool parameters and system boundaries.
