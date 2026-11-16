"""Conservative gate checker on declared facts, NOT an LLM or a product oracle."""
import argparse
import sys
from common import emit, load_json

FLAGS = ("task_known", "structured_rules", "numeric_prediction", "knowledge_required",
         "generation_required", "fixed_steps", "tool_execution", "dynamic_planning",
         "independent_subtasks", "parallel_value_evidence", "conflict_control_ready")


def decide(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    facts = data.get("facts", {})
    if not isinstance(facts, dict):
        raise ValueError("facts must be an object")
    for key, value in facts.items():
        if key not in FLAGS or (value is not None and type(value) is not bool):
            raise ValueError(f"invalid fact {key}: expected boolean or null")
    feasible = data.get("runtime_feasible")
    if feasible is not None and type(feasible) is not bool:
        raise ValueError("runtime_feasible must be boolean or null")
    missing = [k for k in FLAGS if facts.get(k) is None]
    out = {"schema_version": "1.0", "status": "needs_evidence", "base": "unknown",
           "knowledge": "none", "orchestration": "direct", "reasons": [],
           "rejected": [], "missing_evidence": missing}
    if not facts.get("task_known"):
        if feasible is False:
            out["status"] = "blocked"
        out["reasons"].append("任务与成功定义不足；先研究，不推断 AI 收益。")
        return out
    if facts.get("numeric_prediction"):
        out["base"] = "traditional_algorithm"
        out["reasons"].append("目标是数值预测／排序，应先验证统计或传统模型基线。")
    elif facts.get("structured_rules") and not facts.get("generation_required"):
        out["base"] = "rules"
        out["reasons"].append("规则可表达且无需自由生成；确定性实现优先。")
    elif facts.get("generation_required"):
        out["base"] = "llm"
        out["reasons"].append("需要开放语义生成，先验证直接 LLM 基线。")
    elif facts.get("knowledge_required"):
        out["base"] = "retrieval"
        out["reasons"].append("需要定位知识但不需要自由生成，先用可定位的检索。")
    else:
        out["reasons"].append("未证明现有人工／软件基线不足。")
    if facts.get("knowledge_required") and out["base"] == "llm":
        out["knowledge"] = "rag"
    if facts.get("fixed_steps") or facts.get("tool_execution"):
        out["orchestration"] = "workflow"
    # A planner requires both adaptive planning and actual tool execution.
    if facts.get("dynamic_planning") and facts.get("tool_execution"):
        out["orchestration"] = "single_agent"
        if all(facts.get(k) for k in ("independent_subtasks", "parallel_value_evidence", "conflict_control_ready")):
            out["orchestration"] = "multi_agent"
        else:
            out["rejected"].append({"option": "multi_agent", "reason": "独立任务、并行净收益或冲突控制证据不足。"})
    else:
        out["rejected"].append({"option": "single_agent", "reason": "没有同时证明动态规划与工具执行需求。"})
        out["rejected"].append({"option": "multi_agent", "reason": "未满足单 Agent 前置必要性。"})
    if out["base"] == "rules":
        out["rejected"].append({"option": "llm", "reason": "基础任务没有生成需求，模型增加不确定性。"})
    if out["base"] == "unknown" and "base_method" not in missing:
        missing.append("base_method")
    if feasible is None:
        missing.append("runtime_feasible: privacy/budget/latency/dependencies")
    if feasible is False:
        out["status"] = "blocked"
        out["reasons"].append("至少一项硬约束不满足；仅保留条件候选，不允许据此上线。")
    elif not missing:
        out["status"] = "candidate"
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        emit(decide(load_json(args.input)))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"decision error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
