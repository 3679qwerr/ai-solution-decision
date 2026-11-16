# 实际源码研究与设计对比

研究日期：2026-11-16，Asia/Hong_Kong。实际解压并阅读两个 ZIP；不是从 README 或聊天总结推断。研究过程位于工作区 `ai-solution-decision-research`，原包不进入发布包。[源文件清单](source-manifest.json)记录两个归档与 32 个已读文件的 SHA256、路径和行数；这些哈希不冒充 Git commit。

## 1. Johnson44/skill

归档 `skill-main.zip` SHA256：`12eaf2d93528b7578d310cdf4cdbf457f651f2c823ccf190d89433b5fc1bcd18`。

除 README 外，实际读了 hrbp-resume-interview 的 SKILL.md、agents/openai.yaml 和全部四个 references：role-matrix.md、business-models.md、research-protocol.md、output-rubric.md。

入口将真实 JD、公司业务、候选人证据连起来，经任务简报、研究、岗位匹配、诊断与改写、面试表达、真实性检查形成交付。专业知识从角色矩阵、业务链路、研究协议和输出标准按需读取，不把所有材料塞进入口。输出要求“可使用文本+修改依据+待补事实”，不以换关键词代替诊断。研究协议细分官方、原始个案、独立重复与二手线索，不能把个案包装成必然。

可借鉴的是渐进读取、事实约束和价值链映射思想；需要重建的是岗位矩阵、求职研究与 STAR 等领域内容。本项目改为基础方法/知识增强/编排矩阵、产品指标与 MVP，不把求职输出机械改名。

许可证检查：归档只有 README 和该 Skill 资源，没有 LICENSE 或明确授权条款。在线仓库根目录复核也未显示 LICENSE；这不证明所有历史版本都无授权，但足以避免假定再分发权。成品不复制其指令／参考正文、不包含原包；保留方法参考署名。没有将用户称其为“开源”视为许可证证明。

## 2. CZ / NativeHelix

归档 `nativehelix-main.zip` SHA256：`220c6e73270aac16be717a0ec61a9d252e86d7d24a21a2452ec2849286ac2b14`。

三个重点 Skill 的 SKILL.md、references、assets 模板和 agents 元数据均实际阅读；另读了必要性门槛、生命周期成本、多 Agent 子任务、Skill/Trial 评测协议、产品架构能力、基线门槛，以及周报示例的 Workflow 和架构边界。

| 源模块 | 输入和流程 | 输出与专业约束 | 本项目处理 |
|---|---|---|---|
| design-agent-workflow | 产品目标与边界→必要性判断→任务与依赖→状态/工具→评审与停止 | task packet、状态机、人工闸门、恢复；确定性够用时不加 Agent | 改编任务、状态与恢复，融入产品 MVP；不继承跨库 registry 依赖 |
| design-ai-native-architecture | 固定产品使命→产品模式→确定/概率边界→权限→分阶段采纳 | 蓝图、职责、契约、替代方案、成本与晋级证据 | 保留事实/设计分离与硬边界；加入需求洞察和非 AI 方案 |
| review-agent-harness | 追一条执行路径→检查上下文/工具/状态/评测/观测→按证据评级 | findings、阻断与下一阶段证据；设计详细不等于成熟 | 改成产品决策检查与作者自检；不自称独立生产验收 |
| workflow_necessity_gate | hard/soft triggers→需人类选择标准治理路线 | 源项目对建模前审批/注册有特定停点 | 作为研究对象；用户已要求完整开发，本成品不把只读设计强制阻断 |
| skill_evaluation_protocol | 正负触发、同模型配对、确定性与语义评测分层 | 不平均重大安全失败，记录加载归因和试验方差 | 新写 prepare/grade、人工评分通道和 not_run 声明 |
| weekly-project-update-agent 示例 | 用户指定资料→草稿→核对→人工审阅 | 有草稿写入、无传播动作，缺材料不捏造进度 | 用于理解结果与副作用边界，不照搬成营销功能 |

许可证：归档 LICENSE 为 CC BY 4.0；README 明确默认许可与署名 CZ / NativeHelix。改编内容保留原作者、项目链接、完整许可证、修改说明和无背书声明。脚本新写，没有把 CC 文档重新标为 MIT。

源项目跨文件引用并非本项目运行依赖：例如架构资源要求查 `04_Capabilities/CAPABILITY_SOURCE_MAP.yaml`，该归档清单未包含此文件。成品改为完整自包含 references，不能让可安装 Skill 依赖源码库外的治理目录。

## 3. 新增与差异

| 维度 | 参考项目已有 | 本项目新增或重写 |
|---|---|---|
| 产品问题 | 求职证据链；产品/架构分工 | 从模糊需求研究到可验证产品决策闭环 |
| 技术选择 | 最小工作流、Agent 边界 | 非 AI 基线、三层组合、传统算法、RAG 与 Workflow 共存、复杂度升级证据 |
| 可执行性 | 重点三个 Skill 主要为指令、规则与模板 | 标准库成本、门槛、安装、引用验证、对照输入与导入工具 |
| 评测 | 公开协议与检查框架 | 20 题、失败变异检查、手算成本、实际运行日志；未假造模型结果 |
| 产品案例 | 求职；周报草稿 | 营销、小满，完整输入/输出/成本与失败处理 |
| 展示 | 方法和资产目录 | GitHub README、CI、测试局限、来源追踪、源码与安装双 ZIP |

原创是组织、实现和领域适配，不把通用概念本身据为己有。项目开发和确定性测试是实际完成的；需求、业务数字、实验目标与产品架构是模拟示范，不等于真实上线。

## 4. 外部核对来源

归档源码是研究主证据；2026-11-16 另核对 [Johnson44/skill](https://github.com/Johnson44/skill)、[NativeHelix](https://github.com/nickzhuchen66/nativehelix)、[Agent Skills 格式](https://agentskills.io/specification)、[CC BY 4.0 条款说明](https://creativecommons.org/licenses/by/4.0/)。没有用实时 main 替代归档，也没有虚构 archive 对应提交号。许可正文以随包原文为准。
