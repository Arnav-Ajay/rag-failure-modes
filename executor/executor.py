# executor/executor.py
from tools.retrieve_tool import retrieve_tool
from tools.noop import noop_tool

class Executor:
    def execute(self, plan, wm=None):
        execution_trace = []

        for step in plan.steps:
            if not isinstance(step.args, dict):
                raise TypeError(f"Step {step.step_id} args must be a dict")

            TOOL_MAP = {
                "retrieve": retrieve_tool,
                "noop": noop_tool,
            }

            tool_fn = TOOL_MAP.get(step.action)
            if not tool_fn:
                raise ValueError(f"Unknown action: {step.action}")

            result = tool_fn(**step.args)

            if wm is not None:
                wm.thoughts.append(
                    f"Executed step {step.step_id}: {step.action}"
                )

                if step.action == "retrieve":
                    wm.flags["used_retrieval"] = True


            execution_trace.append({
                "step_id": step.step_id,
                "action": step.action,
                "args": step.args,
                "tool_result": result,
                "result_meta": (
                    {"num_chunks": len(result.get("chunks", []))}
                    if isinstance(result, dict)
                    else {}
                ),
            })

        return execution_trace