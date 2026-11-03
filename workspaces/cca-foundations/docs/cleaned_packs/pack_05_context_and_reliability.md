# 📦 Pack 5: Context Management & Reliability

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
  * **Cache Write**: $\approx 1.25\times$ the base input token price (first time).
  * **Cache Read (Hit)**: $\approx 0.10\times$ (90% discount) of the base input token price.
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
    $$T_{\text{wait}} = 2^{\text{attempt}} \times \text{base} + \text{random\_jitter}$$
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