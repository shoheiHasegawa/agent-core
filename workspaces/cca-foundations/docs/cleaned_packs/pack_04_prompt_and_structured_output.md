# 📦 Pack 4: Prompt Engineering & Structured Output

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