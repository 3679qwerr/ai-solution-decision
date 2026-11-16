# AI Solution Decision

从用户问题到可验证的技术选择：**先证明价值，再决定是否需要 AI 与 Agent。**

这是一套面向 AI 产品经理的 Agent Skill。它将需求证据、非 AI 基线、技术取舍、执行边界、MVP 和评测连接成可审阅的决策包。不是营销自动化系统，也没有内置生产工具权限。

## 快速使用

```text
使用 $ai-solution-decision：我们想为销售做一个智能营销 Agent。
现有流程是筛选线索、查产品手册、写邮件草稿并人工发送。
请先判断规则、检索、RAG、Workflow 与 Agent 的必要性，
输出候选取舍、MVP、权限与异常处理、成本假设和评测计划。
没有证据的业务数据请保留未知。
```

输入不用一次写齐。Skill 会将关键事实、条件建议和需要验证的缺口分开，不自动制造用户量或 ROI。

## 核心能力

| 能力 | 实际交付 |
|---|---|
| 需求洞察 | 使用者／付费者、真实任务、现有替代、证据与约束 |
| AI 必要性 | 人工、规则、传统算法、检索与 LLM 基线 |
| 方案选型 | 质量、成本、p95、稳定性、隐私、维护和退出成本 |
| 工作流 | 工具、状态、权限、审批、幂等、恢复、接管与停止 |
| MVP | P0/P1/暂不做、用户流程和可执行验收 |
| 产品评测 | 任务、业务、成本、风险、运行五类指标与对照 |
| 决策解释 | 推荐、拒绝、未知与复杂度升级证据 |

创新在于三层组合：基础方法 × 知识增强 × 编排。RAG 可进入固定 Workflow，多个角色不等于多个 Agent；评分不能抵消隐私或权限硬约束。

## 安装

目录遵循 [Agent Skills 格式](https://agentskills.io/specification)：SKILL.md 含 name/description，支持资料与脚本随目录安装；agents/openai.yaml 提供可选宿主元数据。

1. 保留本目录名 `ai-solution-decision`，复制到目标工具当前文档指定的 Skill 根目录。
2. 或用安装器将它复制到你指定的根目录（拒绝覆盖已有版本）：

```text
python scripts/install.py --skills-dir "D:/my-agent-skills"
```

该示例会得到 `D:/my-agent-skills/ai-solution-decision/SKILL.md`；请把参数换成宿主实际扫描的位置。安装器验证目录和引用，不自动修改宿主配置。按宿主要求刷新或重启后，用 `$ai-solution-decision` 或自然语言调用。不同工具是否识别 `$` 调用和 openai.yaml 以当前文档为准；未宣称所有宿主都已实测。

Skill 阅读本身不依赖 Python；计算、测试和安装器需 **Python 3.10+**，仅用标准库，无 pip 依赖，无密钥或网络要求。Windows 如 `python` 是商店占位符，使用已安装解释器完整路径。Linux/macOS 可按环境用 `python3` 替代。

## 两套完整案例

- [企业智能营销](examples/enterprise-marketing/output.md)：规则筛选、RAG 草稿与人工审批 Workflow。
- [小满桌面伙伴](examples/xiaoman-companion/output.md)：主动交互状态机、许可、情感边界与任务 Skill。

每套均有 [输入与文件说明](examples/README.md)、可运行门槛输入与成本输入输出。**需求和参数均为模拟；没有虚构真实实验成果。**

## 运行与评测

在本目录运行：

```text
python scripts/decision.py --input examples/enterprise-marketing/decision-input.json
python scripts/cost_model.py --input examples/enterprise-marketing/cost-input.json
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/eval_runner.py offline
python scripts/eval_runner.py prepare --output ../trials-001
```

成本模型覆盖有界重试、多调用、工具、人工、固定维护、一次集成和退出，以及 12/36 月 TCO 与调用量敏感性。价格全部显式传入，未知成功率返回 null；不预测延迟，不自动换汇，不包含所有企业特定费用。

[20 个评测案例](evals/cases.json)含非 Agent、正向 Agent、多 Agent 证据门槛、信息不足、隐私冲突、注入、写入超时与范围外任务。[评测协议](evals/PROTOCOL.md)提供可复现有／无 Skill 对照与真实响应导入。离线检查只验证确定性逻辑，不是 LLM 成功率，也不能检测所有语义造假。

交付状态：文件检查、脚本、成本复算、安装与门槛回归已在交付环境执行；准确数量与环境见展示包的测试报告。**模型 A/B、实际宿主自动触发、真实产品效果均未验证。**

## 目录

```text
ai-solution-decision/
├── SKILL.md                 入口与判断边界
├── agents/openai.yaml       元数据
├── references/              选型、业务、研究、控制、输出与评测
├── scripts/                 成本、门槛、安装、验证与评测工具
├── examples/                两套模拟输入和完整决策包
├── evals/                   20 个案例与模型对照协议
├── tests/                   标准库单元与集成测试
├── licenses/                CC BY 4.0 与 MIT 全文
├── ATTRIBUTION.md           来源与修改说明
└── LICENSE                  按文件类别的授权范围
```

## 来源与求职展示边界

研究参考 [Johnson44/skill](https://github.com/Johnson44/skill) 的组织方法，以及 **CZ / NativeHelix** 的 [工作流、架构与 Harness 方法](https://github.com/nickzhuchen66/nativehelix)。NativeHelix 的改编内容保留 CC BY 4.0 署名与修改说明；Johnson44 归档未附许可证，因此不分发其源码或复制正文。具体见 [ATTRIBUTION.md](ATTRIBUTION.md) 与 [LICENSE](LICENSE)。原创脚本和测试为 MIT，文档为 CC BY 4.0。

适合展示的能力是需求拆解、技术取舍、Agent 边界与评测工程。请描述为“开发并验证一套产品决策 Skill”，不要写成“已提高企业转化率”“已验证留存”或“经过独立生产验收”。
