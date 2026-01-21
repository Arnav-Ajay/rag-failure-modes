# planner/planner.py
from decision.decide import decide_retrieval
from planner import Plan, PlanStep

class Planner:
    def generate_plan(self, question: str, *, k: int = 4, wm=None, memory_signal=None) -> Plan:
        decision = decide_retrieval(question)

        memory_advice = (
            memory_signal.get("retrieval_advice")
            if memory_signal else None
        )

        if wm is not None:
            wm.thoughts.append(f"Planner evaluating retrieval need for: {question}")
            if memory_advice:
                wm.thoughts.append("Memory advises retrieval")

        # Planner owns the final decision
        if decision.requires_external_evidence or memory_advice:
            step = PlanStep(
                step_id=1,
                action="retrieve",
                args={"question": question, "k": k},
                rationale=(
                    decision.decision_rationale
                    if decision.requires_external_evidence
                    else "retrieval chosen despite parametric uncertainty due to memory signal"
                ),
            )
        else:
            step = PlanStep(
                step_id=1,
                action="noop",
                args={},
                rationale=decision.decision_rationale,
            )

        return Plan(objective=question, steps=[step])