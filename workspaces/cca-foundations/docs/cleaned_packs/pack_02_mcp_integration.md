# 📦 Pack 2: Tool Design & Model Context Protocol (MCP) Integration

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
| **SSE (Server-Sent Events)** | HTTP POST (client $\to$ server) + HTTP SSE stream (server $\to$ client). | Remote / Cloud-hosted MCP servers. | Requires HTTPS, OAuth 2.1, network firewalls, and token management. |