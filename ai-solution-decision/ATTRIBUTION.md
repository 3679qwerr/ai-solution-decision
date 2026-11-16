# 来源、修改与原创边界

研究基于用户提供的两个 ZIP，日期 2026-11-16（Asia/Hong_Kong）。ZIP 的 SHA256 与逐文件研究清单保存在源码展示包 docs/source-manifest.json；独立安装包不附带两套原始源码。

## CZ / NativeHelix — CC BY 4.0

原项目：[nickzhuchen66/nativehelix](https://github.com/nickzhuchen66/nativehelix)，原署名 **CZ / NativeHelix**。许可证：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，完整原文随包保留于 [licenses/CC-BY-4.0.txt](licenses/CC-BY-4.0.txt)。原始材料无担保；来源作者未背书本项目。

主要研究并改编的路径：

- `05_Skills/cross_functional/design-agent-workflow/{SKILL.md,references/workflow-rules.md,assets/workflow-design-template.md}`：最小流程、状态、副作用、恢复、停止。
- `05_Skills/architect/design-ai-native-architecture/{SKILL.md,references/design-gates.md,assets/architecture-blueprint-template.md}`：事实/设计分离、确定性边界、替代方案与阶段晋级。
- `05_Skills/architect/review-agent-harness/{SKILL.md,references/harness-review-checklist.md,assets/harness-review-template.md}`：权限、上下文污染、工具、观测与成熟度证据。
- `04_Capabilities/technical/05_Evaluation_Engineering/contracts/{skill_evaluation_protocol.md,evaluation_trial_protocol.md}`：配对评测、原始轨迹、重大风险否决。
- `04_Capabilities/technical/10_Operational_Control_Engineering/contracts/lifecycle_cost_gate.md`：全生命周期成本。
- `04_Capabilities/technical/13_Multi_Agent_Coordination/contracts/subagent_job_protocol.md`：隔离任务、合并与取消。
- `04_Capabilities/cross_functional/03_Workflow_Engineering/contracts/workflow_necessity_gate.md`：研究了必要性门槛；未复制其要求先注册审批的治理流程。

修改：将以上概念重新组织为产品经理决策知识，主要体现在 SKILL.md、references/workflow-and-controls.md、references/evaluation.md、references/output-rubric.md 和 evals/PROTOCOL.md。移除源项目角色编制与跨库依赖；不要求冻结 CPO 输入后才允许需求研究；保留现有授权边界，但不把只读设计改成需要反复审批的流程。新增缺失信息处理和分层选型，而非照搬架构模板。

## Johnson44/skill — 归档未附许可证

原项目：[Johnson44/skill](https://github.com/Johnson44/skill)，研究对象为 `hrbp-resume-interview/SKILL.md`、`agents/openai.yaml` 与四个 references：role-matrix、business-models、research-protocol、output-rubric。

借鉴的是“一项 Skill 一个顶层目录、入口按需路由专业知识、研究证据约束、业务价值与输出复核”的组织思想。未复制、翻译或改写其简历／面试指令和参考正文，未将无许可证视作开源再授权。所有本项目产品决策措辞独立编写；原包不进入交付 ZIP。如未来直接复用表达性内容，应先核实权利人授权。

## 本项目新增

三层技术组合、非 AI 基线与复杂度升级门槛；保留未知的可执行门槛检查器；有界重试与人工复核 TCO 计算；两套完整模拟案例；20 个评测输入；隔离双组提示生成与响应导入；重大风险否决的人工评分通道；标准库测试、复制安装器与 CI。

不声称原创 Agent 状态机、RAG、TCO 或通用 A/B 方法本身；原创部分是本任务的领域组织、具体实现、案例和评测工件。作者贡献说明应保持为实际研究、设计和验证工作，不能写成生产落地成果。
