# `rag-failure-modes`

## Why This Repository Exists

This repository exists to deliberately surface, isolate, and classify **failure modes in retrieval-augmented and agentic systems** — not to fix them, optimize them, or obscure them behind heuristics.

> **A system you cannot explain when it fails is not a system — it is a liability.**

Most RAG work focuses on improving answers.
This repository focuses on understanding *why* answers fail.

---

## What Problem This Repository Addresses

Modern RAG and agentic systems fail in ways that are:

* Silent
* Confounded across layers
* Incorrectly attributed (retrieval vs planning vs ranking vs evidence vs memory)
* “Solved” with patches instead of understanding

This repository asks a different question:

> **When a system produces a bad outcome, which layer failed — and how can we prove it?**

---

## Core Thesis (Failure-First Framing)

This repository treats **failure as the primary signal**, not success.

Concretely:

* Failures are **intentionally induced**
* Failures are **not immediately fixed**
* Failures are **logged, classified, and traced**
* Optimization is explicitly deferred

Understanding failure *precedes* improving performance.

---

## What This Repository Explicitly Does NOT Do

This is **not** a tuning or mitigation repository.

It deliberately avoids:

* Prompt engineering
* Retrieval optimization
* Reranking optimization
* Memory heuristics
* Guardrails as “fixes”
* Aggregate accuracy metrics

If the system breaks here, that is **desirable**.

---

## System Lineage (Assumed and Frozen)

This repository assumes a **pre-existing, frozen system stack** built in earlier work.
No new intelligence is added here.

### Foundations (Retrieval & Representation)

**Repository:**
[`rag-systems-foundations`](https://github.com/Arnav-Ajay/rag-systems-foundations)

Covers:

* Chunking strategies
* Dense / sparse / hybrid retrieval
* Reranking primitives
* Retrieval evaluation discipline

### Agent Architecture (Decision, Execution, Memory, Policy)

**Repository:**
[`agent-systems-core`](https://github.com/Arnav-Ajay/agent-systems-core)

Covers:

* Tool-using agents
* Planner / executor separation
* Memory systems (episodic + semantic)
* Policy-driven overrides

**All components from these repositories are treated as immutable inputs.**

This repository adds **visibility, not capability**.

---

## Scope of Analysis in This Repository

Failures are isolated **layer by layer**, rather than treating the system as a monolith.

---

## Layers Examined

### 1. Retrieval Layer

Failures where:

* Relevant evidence is missing
* Evidence exists but is ranked out
* Hybrid retrieval biases suppress correct chunks
* Cross-document recall pollution occurs

Retrieval is analyzed **independently**, without planner, executor, policy, or evidence intervention.

---

### 2. Reranking Layer

Failures where:

* Gold evidence is retrieved but not promoted
* Ranking remains unchanged despite richer candidate pools
* Reranking fails to resolve hybrid retrieval bias
* Retrieval and reranked outputs are identical despite added signal

**Key observation:**

> Reranking can improve gold-chunk rank, but does not guarantee evidence sufficiency.

Reranking is treated as a **distinct failure surface**, not a retrieval fix.

---

### 3. Planner Layer

Failures where:

* Retrieval is skipped when mandatory
* Retrieval is invoked when unnecessary
* Ambiguous questions are misclassified
* Logged rationale does not justify the decision

Planner analysis focuses on **decision correctness**, not answer quality.

---

### 4. Executor Layer

Failures where:

* Planned actions are not faithfully executed
* Tools are mis-invoked
* Arguments are ignored or malformed
* Retrieved context is dropped or mishandled

**Finding:**
Executor failures are structurally rare due to:

* Single-step plans
* Deterministic tool dispatch
* Absence of downstream transformation

This absence is an **architectural property**, not an oversight.

---

### 5. Evidence Assessment Layer

Failures where:

* Evidence is judged sufficient despite weak or absent support
* Evidence is judged insufficient despite being present
* Sparse evidence is treated as decisive
* Conflicting evidence is not detected
* Evidence assessment is computed but not respected downstream

**Key finding:**

> Even when retrieval and reranking succeed, evidence assessment can still (correctly) refuse due to ambiguity, dilution, or low signal strength.

This layer cleanly separates:

* *Was something retrieved?*
* *Was the right thing ranked?*
* *Is the available evidence actually sufficient?*

---

### 6. Memory Layer

Failures where:

* Semantic or episodic memory influences decisions when it should not
* Information leaks across questions
* Semantic memory is treated as authoritative
* Memory-based policy signals are ignored
* Memory writes occur silently
* Memory influences behavior without trace attribution

**Finding:**
Under baseline conditions, memory failures are structurally rare due to causal isolation.

This establishes a **clean baseline** before policy pressure.

---

### 7. Policy Layer

Failures where:

* Policy overrides planner decisions incorrectly
* Retrieval is forced for parametric questions
* Policy fires on stale or insufficient evidence
* Planner rationale contradicts applied policy
* Policy influence is not traceable in logs

**Finding:**
Policy is the first layer to **intentionally reintroduce coupling** — and therefore the first to reintroduce failure after isolation.

---

### 8. Generation Layer

Failures where:

* Answers are produced despite conflicting or insufficient evidence
* Uncertainty is collapsed into over-confident language
* Evidence sufficiency signals are ignored
* Refusal or hedge policies are bypassed

**Key finding:**

> Improved retrieval and ranking do not guarantee answerability — generation must respect epistemic state, not just context availability.

Generation failures are **epistemic**, not stylistic.

---

### 9. Generation Policy

Failures where:

* Hedge is treated as a stylistic soft answer instead of a terminal action
* Refusal thresholds are bypassed
* Policy decisions are overridden implicitly by generation

**Finding:**
Policy-aware generation is the final enforcement point — failures here invalidate all upstream correctness.

---

## Failure Taxonomy Philosophy

Failure modes are:

* **Layer-specific**
* **Mutually exclusive**
* **Causally attributable**

A failure is assigned to **exactly one layer**, even if downstream effects exist.

Correct outputs produced for incorrect reasons are treated as **failures**, not successes.

---

## Artifacts Produced

This repository produces **diagnostic artifacts**, not metrics:

* Per-layer execution traces (JSON):
  `artifacts/failure_cases/traces`
* Layer-specific question sets:
  `artifacts/failure_cases/questions`
* Layer-specific result sheets:
  `artifacts/failure_cases/results`

There is **no single evaluation score**.

---

## System Contract

### Inputs

* Deterministic question sets
* Known-answer and known-unanswerable prompts
* Ambiguous boundary cases
* Contradictory and adversarial inputs

### Outputs

* Planner decision traces
* Reranker and evidence assessment traces
* Memory and policy influence traces
* Generation behavior traces
* Explicit failure attribution

### Non-Goal

* Improving answer accuracy

---

## Relationship to Observability Work

This repository answers:

> **What kinds of failures exist in principle?**

A separate repository —
[`llm-observability-logs`](https://github.com/Arnav-Ajay/llm-observability-logs) — will answer:

> **How do we observe and monitor these failures reliably in production systems?**

Failure definition precedes observability instrumentation.

---