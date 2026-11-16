# 完整决策包与机器输出契约

## 可读决策包

1. **决策摘要**：用户任务、推荐组合、当前阶段、为什么更简单方案足够／不够。
2. **需求证据**：使用者／付费者、当前替代、痛点、目标、约束、证据台账与未知。
3. **候选比较**：至少覆盖非 AI 基线、推荐项与最强替代；必要时逐一排除八类技术。六维比较不明项写 unknown。
4. **方案与控制**：数据流、工具、状态、权限、审批、异常、降级、停止线和人工接管；不需要 Agent 时明确说明。
5. **MVP**：P0/P1/暂不做、用户流程、依赖、交付角色与 Given/When/Then 验收。
6. **评测与经济性**：指标卡、对照／消融、成本输入与假设、预算、阶段晋级条件。
7. **决策日志**：拒绝的选项及依据、假设、未决问题、否决／升级触发器、下一步责任人。

## 可机器检查的输出

完整文本用于阅读；模型对照评测额外返回单个 JSON 对象，字段如下。schema_version 固定为 1.0；不可从脚本 candidate 推断用户批准。

```json
{
  "schema_version": "1.0",
  "case_id": "由评测输入提供",
  "should_trigger": true,
  "recommendation": {"base": "llm", "knowledge": "rag", "orchestration": "workflow", "status": "needs_evidence"},
  "rationale": "结合任务事实解释最小充分方案和升级条件",
  "rejected_options": [{"option": "multi_agent", "reason": "说明不满足的事实与代价"}],
  "evidence": [{"claim": "关键事实或未知", "role": "unknown", "source": "未提供", "limitation": "如何验证"}],
  "mvp": {"p0": ["核心闭环"], "out_of_scope": ["暂不做"], "user_flow": ["入口", "结果"], "acceptance": ["Given 输入，When 操作，Then 可验证结果"]},
  "metrics": [{"category": "task", "name": "任务成功率", "definition": "验收成功/有效分配", "window": "拟议评测批次", "source": "脱敏事件", "owner": "产品", "target_role": "proposed"}],
  "controls": {"permissions": "工具与资源范围", "approval": "副作用的具体授权边界", "failure": "失败分类与处理", "fallback": "人工或简化方案", "stop": "预算/时间/取消停止线"},
  "unknowns": ["没有真实基线与实验结果"],
  "experiment": "对照组、随机单位、数据来源、晋级和停止条件"
}
```

`base` 枚举 `manual/rules/traditional_algorithm/retrieval/llm/unknown`；knowledge 为 `none/rag`；orchestration 为 `direct/workflow/single_agent/multi_agent`；status 为 `candidate/needs_evidence/blocked`。RAG 要求 base=llm；Agent 要有动态工具路径的解释。五类 metrics 为 `task/business/cost/risk/operations`。evidence.role 见研究规范；target_role 为 `observed/proposed/simulated/unknown`。

对于 should_trigger=false 的任务，最小输出 `schema_version/case_id/should_trigger/rationale` 即可，不强迫用户做产品研究。评测器拒绝缺字段和非法类型；结构通过并不代表内容真实或方案正确。手工评分必须另查证据和语义。
