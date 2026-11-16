# 两套完整案例

全部为**模拟需求与设计示范**，不是对同名真实产品的审计；不代表已有用户研究、系统实现或线上成绩。输出中的数字是拟议目标或模拟参数，真实业务效果均 unknown。每套含原始输入、完整决策包、门槛检查输入和可复算成本。

| 案例 | 核心选择 | 文件 |
|---|---|---|
| 企业智能营销 | 规则分层 + RAG 草稿 + 固定审批 Workflow；MVP 不用自治 Agent | [输入](enterprise-marketing/input.md) · [输出](enterprise-marketing/output.md) |
| 小满桌面伙伴 | 本地状态机 + 可选 LLM + 任务 Skill；不推断真实心理状态 | [输入](xiaoman-companion/input.md) · [输出](xiaoman-companion/output.md) |

复算示例：`python scripts/cost_model.py --input examples/enterprise-marketing/cost-input.json`。`cost-output.json` 是脚本对模拟输入的实际计算结果，不能称为实际账单。
