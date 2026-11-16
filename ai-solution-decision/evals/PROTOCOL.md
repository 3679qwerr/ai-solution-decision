# 可复现评测：离线与模型对照分开

## 已提供的层级

1. `validate.py`：文件、JSON、引用与示例完整性。
2. `unittest`：手算成本、不合法输入、未知／硬约束、多 Agent 门槛、安装、评测器变异测试。
3. `eval_runner.py offline`：对 cases.json 的显式事实执行确定性门槛回归。它不调用模型，不测试自然语言理解，也不证明 Skill 自动触发。
4. `prepare/grade`：生成相同任务的 baseline／with_skill 输入，导入真实模型输出并验证结构与冻结 oracle；另导入人工八维评分。
5. 宿主集成和真实业务对照：需要模型、受控工具与真实数据，当前未运行。结构字段无法证明工具权限实际生效。

## 复现命令

在 Skill 根目录，Python 3.10+，标准库即可：

```text
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/eval_runner.py offline
python scripts/eval_runner.py prepare --output ../trials-001
python scripts/eval_runner.py grade --responses ../responses.json --reviews ../reviews.json
```

prepare 不调用 API、不花费模型费用；输出已存在则拒绝覆盖。不要把合成单元测试响应作为模型响应导入来报告效果。

## 模型调用步骤

- 固定模型精确版本、配置、最大输出、工具权限、环境与 Skill 文件哈希。每题每组建议至少 3 次独立会话（最初设计值，非充分样本量保证），顺序随机化，保留失败与超时。
- 将 prepare 生成的 `.baseline.txt` 或 `.with_skill.txt` 作为用户消息，system 提示两组相同。不要给模型 `cases.json`、expected、评分结果、测试文件或示例答案。baseline 不能自动发现当前安装的 Skill，最好在没有该目录的隔离会话执行。
- 两组共享输出格式，意味着测量的是统一格式条件下的决策改进，不能声称完全无提示基线。with_skill 是显式注入内容的对照，不能声称已验证某宿主自动发现／渐进加载；真实宿主加载需另外保存调用轨迹。
- 每次保存原始响应、规范化 JSON、run_id、时间、模型、配置 hash、token、latency、actual cost（未知为 null）、trace_ref。API 适配由评测者选定工具实现；本包不读取凭证，不默认调用供应商。
- JSON 解析失败保留原文，导入 response=null 记录失败，不静默修复后声称通过。工具超时／越权必须记录在轨迹中，最终文本不是执行证据。

导入格式是 JSON 数组，实际测量填 telemetry；此示意不构成运行记录：

```json
[
  {
    "case_id": "D01",
    "arm": "with_skill",
    "repeat": 1,
    "response": null,
    "telemetry": {"model": null, "config_hash": null, "input_tokens": null, "output_tokens": null, "latency_ms": null, "cost": null, "trace_ref": null}
  }
]
```

人工 reviews 为数组，每项含 case_id/arm/repeat/reviewer/evidence_notes/critical_failure 以及 scores（problem、selection、evidence、tradeoffs、workflow、mvp、evaluation、explanation 各 0–2），评分说明见 [标准](../references/output-rubric.md)。评审应看原始输入与证据，并隐藏 arm。作者自评可用于修订，但不能标独立验收。grade 分开报告结构／oracle 检查、缺失配对、缺失题与人工评分；有缺失时总 passed 为 false，结构通过不能填补未测证据。即便总 passed=true 也不自动晋级。

## 报告与决策

逐 case 配对报告结构通过、决策一致、八维质量、token/成本/耗时以及关键安全失败。人工发现虚构数据、无授权副作用、注入服从或隐私泄漏立即否决；离线检查不宣称识别所有语义造假。

正负触发混淆矩阵：TP/FP/FN/TN，precision=TP/(TP+FP)，recall=TP/(TP+FN)，分母 0 为 unknown。这里首先测模型对 should_trigger 的响应，真实宿主调用另报。按任务分层统计成对差和跨重复方差，报告缺失对，不选择最好一次。小样本仅 smoke，不推导普适效果；没有调用时 baseline delta、置信区间和真实业务改进均为 not_run／unknown。

先用作者案例调试，然后新增盲测、真实失败与宿主故障注入；当前案例不是独立盲测集，不能用全通过宣称泛化。任何明确需求允许多种方案时先审查 oracle，而不是强迫模型追随错误答案。
