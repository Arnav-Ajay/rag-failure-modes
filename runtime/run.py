# runtime/run.py
from planner import Planner
from executor import Executor
from response.generate import Generator
from utils import write_trace
from memory import MemoryRouter
from memory.working import WorkingMemory
from policies.retrieval_policy import allow_retrieval
from policies.write_filter import allow_semantic_write
from policies.forgetting import apply_forgetting

from dataclasses import asdict

class Runtime:
    def _serialize_plan(self, plan):
        return asdict(plan)

    def run(self, question: str, *, k: int = 4, enforce_policies: bool = False):
        mem = MemoryRouter()
        wm = WorkingMemory()
        wm.goal = question

        last_user_question = mem.read_semantic("last_user_question")
        recent_episodes = mem.read_recent_episodes(n=10)

        force = False
        if enforce_policies:
            recent_episodes = apply_forgetting(recent_episodes)
            force = allow_retrieval(wm=wm, episodic_tail=recent_episodes)
    
        planner = Planner()
        memory_signal={
            "retrieval_advice": force,
            "policy_enforced": enforce_policies
        }

        plan = planner.generate_plan(question, k=k, wm=wm,
                                     memory_signal=memory_signal)
        
        executor = Executor()
        execution_trace = executor.execute(plan, wm=wm)

        retrieved_context = ""
        for step in execution_trace:
            if step["action"] != "retrieve":
                continue
            tool_result = step.get("tool_result", {})
            all_chunks = tool_result.get("chunks", [])

            retrieved_context = "\n\n".join(
                f"[{c.get('chunk_id', '?')}] {c.get('text', '')}"
                for c in all_chunks[:k]
            )

        answer = Generator().generate_answer(question, retrieved_context)

        if not enforce_policies or allow_semantic_write("last_user_question", question, wm=wm, episodic_tail=recent_episodes):
            mem.write_semantic("last_user_question", question)
        if not enforce_policies or allow_semantic_write("last_answer_perview", answer[:200], wm=wm, episodic_tail=recent_episodes):
            mem.write_semantic("last_answer_perview", answer[:200])

        mem.write_episodic({
            "ts_utc": __import__("time").time(),
            "question": question,
            "plan_actions": [s.action for s in plan.steps],
            "used_retrieval": any(s["action"] == "retrieve" for s in execution_trace),
            "last_user_question_before_run": last_user_question,
            "recent_episodes_count_before_run": len(recent_episodes),
        })

        write_trace({
            "question": question,
            "plan": self._serialize_plan(plan),
            "execution": execution_trace,
            "final_answer": answer,
            "memory": {
                "semantic_reads": {"last_user_question": last_user_question},
                "episodic_reads": {"recent_episodes_n": len(recent_episodes)},
                "semantic_writes": ["last_user_question", "last_answer_preview"],
                "episodic_writes": "append",
            },
            "working_memory": {
                "goal": wm.goal,
                "thoughts": wm.thoughts,
                "flags": wm.flags,
            },
            "policy_mode": {
                "retrieval_advice": force,
                "policy_enforced": enforce_policies
            }
        })

        return answer