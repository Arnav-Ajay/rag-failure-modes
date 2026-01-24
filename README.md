# `rag-failure-modes`

## Why This Repository Exists

This repository exists to deliberately surface, isolate, and classify **failure modes in retrieval-augmented and agentic systems** — not to fix them, optimize them, or obscure them behind heuristics.

> **A system you cannot explain when it fails is not a system — it is a liability.**

Most RAG work focuses on improving answers.
This repository focuses on understanding *why* answers fail.

---

## What Problem This Repository Addresses

Modern RAG systems fail in ways that are:

* Silent
* Confounded across layers
* Incorrectly attributed (retrieval vs planning vs execution vs memory)
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
* Reranking improvements
* Memory heuristics
* Guardrails or refusal logic
* Aggregate accuracy metrics

If the system breaks here, that is **desirable**.

---

## System Lineage (Assumed and Frozen)

This repository assumes a **pre-existing, frozen system stack** built in earlier work. No new intelligence is added here.

### Foundations (Retrieval & Representation)

* **Repository**:
  [`rag-systems-foundations`](https://github.com/Arnav-Ajay/rag-systems-foundations)
  Covers:

  * Chunking strategies
  * Dense / sparse / hybrid retrieval
  * Reranking
  * Retrieval evaluation discipline

### Agent Architecture (Decision, Execution, Memory)

* **Repository**:
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

This repository isolates failures **layer by layer**, rather than treating the system as a monolith.

### Layers Examined (So Far)

#### 1. Retrieval Layer

Failures where:

* Relevant evidence is missing
* Evidence exists but is ranked out
* Hybrid retrieval biases suppress correct chunks
* Cross-document pollution occurs

Retrieval is analyzed *without* changing planner or executor behavior.

---

#### 2. Planner Layer

Failures where:

* Retrieval is skipped when mandatory
* Retrieval is invoked when unnecessary
* Ambiguous questions are misclassified
* Logged rationale does not justify the decision

Planner analysis focuses on **decision correctness**, not answer quality.

---

#### 3. Executor Layer

Failures where:

* Planned actions are not faithfully executed
* Tools are mis-invoked
* Arguments are ignored or malformed
* Retrieved context is dropped or mishandled

**Finding:**
In the current architecture, executor failures are structurally rare due to:

* Single-step plans
* Deterministic tool dispatch
* Absence of downstream generation or transformation

This absence is itself an architectural property, not an oversight.

---

## Failure Taxonomy Philosophy

Failure modes are:

* **Layer-specific**
* **Mutually exclusive**
* **Causally attributable**

A failure is assigned to **exactly one layer**, even if downstream effects exist.

Examples of failure classes under investigation include:

* Retrieval skipped despite source-bound question
* Retrieval invoked for purely parametric queries
* Planner confidence collapse under ambiguity
* Executor obedience masking planner mistakes
* Correct answers produced for incorrect reasons

These are **working classifications**, not final conclusions.

---

## Artifacts Produced

This repository produces **diagnostic artifacts**, not scores:

* Per-layer execution traces (JSON): `artifacts\failure_cases\traces`
* Layer-specific question sets: `artifacts\failure_cases\questions`
* Layer-specific result sheets: `artifacts\failure_cases\results`

There is **no single evaluation metric**.

---

## System Contract

### Inputs

* Deterministic question sets
* Known-answer and known-unanswerable prompts
* Ambiguous boundary cases
* Contradictory and adversarial inputs

### Outputs

* Planner decision traces
* Executor execution traces
* Failure mode attribution
* Explicit “ambiguous / undecidable” buckets

### Non-Goal

* Improving answer accuracy

---

## Relationship to Observability Work

This repository answers:

> **What kinds of failures exist in principle?**

A separate repository (`llm-observability-logs`) will address:

> **How do we observe and monitor these failures reliably in production systems?**

Failure definition precedes observability instrumentation.

---

## Status

🚧 **Active analysis**

* Retrieval, planner, and executor layers analyzed
* Failure modes defined and exercised
* Memory and policy influence intentionally deferred
* No system changes introduced

This repository will only move forward once each layer’s failure surface is understood.

---