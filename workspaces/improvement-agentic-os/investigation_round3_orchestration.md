# Investigation Round 3: Orchestration Refactoring

## 1. Introduction: Fat Orchestration vs. Thin Orchestrator + Blackboard (PubSub)
Currently, the system relies on a **Fat Orchestration** model where agents call other sub-agents synchronously (Daisy Chain) and block while waiting for responses. This creates deep call stacks, tightly couples agents, and limits scalability and fault tolerance. 

The goal is to migrate to a **Thin Orchestrator + Blackboard (PubSub)** model. In this architecture:
- **Thin Orchestrator**: Manages the overarching workflow and lifecycle but does not contain complex business logic or block on sub-agent execution.
- **Blackboard (PubSub)**: A centralized message bus where tasks, state updates, and results are published. Agents subscribe to topics relevant to their skills, process tasks asynchronously, and publish results back to the blackboard.

## 2. Refactoring Existing SKILLs and Routing Logic
To adapt to the PubSub model, existing SKILLs and routing mechanisms must be decoupled:

### 2.1 Skill Refactoring
- **Stateless Execution**: Skills must be modified to become stateless event handlers. They should consume an event (task) from the blackboard, perform their function, and emit a result event.
- **Payload Standardization**: Introduce a standardized event schema (e.g., CloudEvents) for all SKILL inputs and outputs.
- **Asynchronous Handlers**: Remove blocking `wait()` or synchronous RPC calls within SKILLs. Instead of waiting for a dependency, a SKILL should emit a request event and terminate, or park its state until a response event triggers a continuation.

### 2.2 Routing Logic Refactoring
- **From Direct Invocation to Topic-Based Routing**: Replace direct function or agent calls with message publishing. For example, instead of `agent_A.call(agent_B)`, `agent_A` publishes to the `task.agent_B.requested` topic.
- **Dynamic Subscription**: Agents (or the orchestrator) dynamically subscribe to topics based on their capabilities, allowing for more flexible routing and load balancing.

## 3. System Deadlock Risks During Transition
During a phased migration where both synchronous (Fat) and asynchronous (Thin/PubSub) models coexist, several deadlock risks emerge:

- **Mixed-Mode Blocking**: If a legacy synchronous agent calls a refactored asynchronous agent and waits for a direct return value (which will now arrive via the blackboard), the legacy agent will block forever.
- **Thread/Resource Exhaustion**: Synchronous agents blocked waiting for PubSub events might tie up worker threads, preventing new events from being processed and causing a system-wide deadlock.
- **Circular Dependencies**: In the PubSub model, poorly configured event triggers could cause an infinite loop of events, or two agents waiting on events from each other without a timeout mechanism.

## 4. Safe, Incremental Migration Path
To mitigate these risks, the migration should follow the Strangler Fig pattern:

### Phase 1: Infrastructure and Dual-Write
1. **Deploy the Blackboard (PubSub)**: Introduce the message broker (e.g., Redis PubSub, Kafka, or an internal event bus).
2. **Event Emitting (Shadowing)**: Modify existing Fat Orchestrator agents to publish events to the blackboard *in addition* to their synchronous calls, without acting on the events yet. This allows monitoring of the event flow.

### Phase 2: Adapter Layer (The Bridge)
1. **Implement Sync-to-Async Adapters**: Create wrappers for legacy agents that translate a synchronous call into a PubSub publish, wait for the corresponding result event on the blackboard, and return it synchronously. 
2. **Implement Async-to-Sync Adapters**: Allow new PubSub agents to call legacy synchronous agents by wrapping the legacy call in a worker that publishes the result to the blackboard upon completion.

### Phase 3: Incremental Refactoring of SKILLs
1. **Leaf Nodes First**: Identify "leaf" SKILLs (agents that do not call other agents) and refactor them to be purely event-driven.
2. **Update Callers**: Update the agents that call these leaf nodes to use the PubSub model or the Sync-to-Async adapter.
3. **Move Up the Tree**: Progressively refactor higher-level orchestrator logic from synchronous chains to event-driven orchestrators (e.g., using Sagas or state machines).

### Phase 4: Deprecation of Fat Orchestration
1. Once all agents are communicating via the blackboard, remove the Sync-to-Async adapters.
2. Decommission the legacy direct-invocation pathways.
3. Enforce strict timeouts and dead-letter queues (DLQs) on the blackboard to handle any lingering stalled processes gracefully.
