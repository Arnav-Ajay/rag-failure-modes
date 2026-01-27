# runtime/run.py
from planner import Planner
from executor import Executor
# from response.generate import Generator
from utils.logging_utils import write_trace
from memory import MemoryRouter
from memory.working import WorkingMemory
from policies.retrieval_policy import allow_retrieval
from policies.write_filter import allow_semantic_write
from policies.forgetting import apply_forgetting
from policies.generation_policy import GenerationPolicy
from generator.generator import Generator
from evidence import EvidenceAssessor
from dataclasses import asdict

class Runtime:
    def _serialize_plan(self, plan):
        return asdict(plan)

    def run(self, question: str, *, k: int = 4, enforce_policies: bool = True):
        mem = MemoryRouter()
        wm = WorkingMemory()
        wm.goal = question
        
        # First step: prove persistence exists and is auditable.
        last_user_question = mem.read_semantic("last_user_question")
        recent_episodes = mem.read_recent_episodic(n=10)
        if enforce_policies:
            recent_episodes = apply_forgetting(recent_episodes)
            force = allow_retrieval(wm=wm, episodic_tail=recent_episodes)
        else:
            force = False

        planner = Planner()
        plan = planner.generate_plan(question, k=k, wm=wm, memory_signal={"force_retrieval": force is True})

        executor = Executor()
        execution_trace = executor.execute(plan, wm=wm)
        # NOTE: If multiple retrieve steps exist, the last one wins by design.

        retrieved_context = ""
        executor_decision = "noop"
        for step in execution_trace:
            executor_decision = step["action"]
            if executor_decision != "retrieve":
                continue

            tool_result = step.get("tool_result", {})
            all_chunks = tool_result.get("chunks", [])
            # cid, doc_id, text, score
            retrieved_context = "\n\n".join(
                f"[{c.get('chunk_id', '?')}] {c.get('text', '')}"
                for c in all_chunks[:k]
            )

        # right after the loop where you set executor_decision and all_chunks
        chunks_for_evidence = execution_trace[0].get("tool_result", {}).get("chunks", []) if executor_decision == "retrieve" else []
        evidence_assessment = EvidenceAssessor().assess_evidence(
            query=question,
            executor_decision=executor_decision,
            retrieved_chunks=chunks_for_evidence,
        )

        generation_decision = GenerationPolicy.decide(evidence_assessment)

        generator = Generator()
        answer = generator.generate(
            question=question,
            context=retrieved_context,
            decision=generation_decision,
            llm_call=lambda p: "<LLM_CALL_PLACEHOLDER>",
        )


        if not enforce_policies or allow_semantic_write("last_user_question", question, wm=wm, episodic_tail=recent_episodes):
            mem.write_semantic("last_user_question", question)
        if not enforce_policies or allow_semantic_write("last_answer_preview", answer[:200], wm=wm, episodic_tail=recent_episodes):
            mem.write_semantic("last_answer_preview", answer[:200])

        mem.write_episodic({
            "ts_utc": __import__("time").time(),
            "question": question,
            "plan_actions": [s.action for s in plan.steps],
            "used_retrieval": any(s["action"] == "retrieve" for s in execution_trace),
            "last_user_question_before_run": last_user_question,
            "recent_episode_count_before_run": len(recent_episodes),
            "event": "evidence_assessment",
            "executor_decision": executor_decision,
            "evidence_assessment": evidence_assessment.__dict__,
            "generation_policy_decision": generation_decision.decision,
            "produced_text": answer is not None,
        })

        write_trace({
            "question": question,
            "plan": self._serialize_plan(plan),
            "execution": execution_trace,
            "evidence_assessment": evidence_assessment.__dict__,
            "generation_decision": {
                "decision": generation_decision.decision,
                "refusal_code": (
                    generation_decision.refusal_code.value
                    if generation_decision.refusal_code else None
                ),
                "hedge_code": (
                    generation_decision.hedge_code.value
                    if generation_decision.hedge_code else None
                ),
                "rationale": generation_decision.rationale,
            },
            "final_answer": answer,
            "memory": {
                "semantic_reads": {"last_user_question": last_user_question},
                "episodic_reads": {"recent_episodes_n": len(recent_episodes)},
                "semantic_writes": ["last_user_question", "last_answer_preview"],
                "episodic_write": "append",
            },
            "working_memory": {
                "goal": wm.goal,
                "thoughts": wm.thoughts,
                "flags": wm.flags,
            },
            "policy_mode": enforce_policies,
        })

        return answer
