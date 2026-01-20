# `rag-failure-modes`

## Why This Repository Exists

This repository exists to deliberately surface, isolate, and classify **RAG failure modes** — not to fix them, optimize them, or hide them behind heuristics.

> **A system you can’t explain when it fails is not a system — it’s a liability.**

---

## What Problem This Repository Addresses

Most RAG systems fail in ways that are:

* Silent
* Confounded across layers
* Incorrectly attributed (retrieval vs generation vs memory)
* “Solved” with hacks instead of understanding

This repository asks a different question:

> **When a RAG system gives a bad answer, *which layer failed*, and *how do we know*?**

---

## Core Thesis (Failure-First Framing)

This repository treats **failure as the primary signal**, not success.

Specifically:

* We **intentionally induce failures**
* We **do not fix them immediately**
* We **log, classify, and reason about them**

Optimization comes *later* (Weeks 10–12).

---

## What This Repository Explicitly Does NOT Do

This is **not** a mitigation or tuning repo.

It deliberately avoids:

* Prompt engineering fixes
* Reranking improvements
* Retrieval tuning
* Memory heuristics
* “Guardrail” band-aids
* Evaluation score chasing

If the system breaks, that is **desirable** here.

---

## System Lineage (How This Builds on Prior Weeks)

This repository assumes the full stack from prior repositories exists and is frozen:

* [`agent-tool-retriever`](https://github.com/Arnav-Ajay/agent-tool-retriever): Tool-using agent
* [`agent-planner-executor`](https://github.com/Arnav-Ajay/agent-planner-executor): Planner / executor separation
* [`agent-memory-systems`](https://github.com/Arnav-Ajay/agent-memory-systems): Short-term + long-term memory

**No new intelligence is added.**

Only **new visibility into failure**.

---

## Failure Classes Under Investigation (Initial Hypothesis)

This repository will investigate — but not yet conclude — failures such as:

* **Retrieval-present but ignored**
* **Retrieval-absent but answerable via parametric knowledge**
* **Planner chooses retrieval when it shouldn’t**
* **Planner skips retrieval when it must not**
* **Executor answers despite insufficient evidence**
* **Memory contamination across sessions**
* **Contradictory retrieved contexts**
* **High-confidence wrong answers**
* **Correct answers for the wrong reasons**

These are *working hypotheses*, not finalized taxonomy.

---

## System Contract (Planned)

**Inputs**

* Deterministic query sets
* Known-answer and known-unanswerable questions
* Contradictory and adversarial prompts
* Memory-carryover scenarios

**Outputs**

* Layer-specific traces
* Failure annotations
* Structured logs (not metrics yet)
* Human-readable failure narratives

**Non-goal**

* Improving answer accuracy

---

## Planned Evaluation Artifacts (No Results Yet)

This repository is expected to produce:

* A **failure-mode taxonomy**
* Per-layer failure attribution
* Example traces demonstrating:

  * Same answer, different failure causes
  * Different answers, same failure cause
* Explicit “unknown / ambiguous” buckets

Nothing here will be summarized as a single score.

---

## Status

🚧 **Planning phase**

* No results yet
* No conclusions yet
* Architecture intentionally conservative
* Instrumentation decisions deferred to `llm-observability-logs`

---

## Relationship to other repositories (Observability)

This repository answers:

> **What kinds of failures exist?**

`llm-observability-logs` answers:

> **How do we observe them reliably in production?**

---