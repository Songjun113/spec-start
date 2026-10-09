# Spec 文件与迁移约定

## 一份需求真源

默认结构：
- `spec/project.md`：目标、范围、明确不在本次交付的内容、阶段依赖、入口。
- `spec/requirements.json`：当前需求及验收状态的唯一真源。脚本只接受 schema_version=1。
- `spec/tasks.md`：可执行任务、需求编号、负责人/实现位置、验证与停止条件。
- `spec/decisions.md`：需求解释与合同变更的依据，不是重复实验流水账。
- `spec/status.md`：从需求清单生成的当前快照；手改会在 refresh 时被替换。
- `PROJECT.md`：导航。已有正文和台账保留，原计划、实验记录及审计材料只作对应证据，不复制成长篇新规范。

## requirements.json 的字段

`project` 包含 name、objective、updated_at、scope_review（draft/confirmed）。`requirements` 是需求数组，每项包含：

| 字段 | 用法 |
|---|---|
| id / title / requirement | 稳定 r001 等编号、简称、实际用户需求 |
| source | 用户指令或有效合同的定位，不能填“系统默认”冒充确认 |
| priority / required | 先后顺序与本次是否必需；不得为了显示完成擅改 required |
| status | planned、in_progress、awaiting_user、blocked、verified、deferred |
| interpretation | state=confirmed/proposed/ambiguous；statement 写可检查解释；source 写解释依据 |
| acceptance | 各验收点 id/text/status；status=pending/partial/failed/verified；evidence 列表 |
| implementation | 相关代码、数据、配置路径；不存在的计划产物应在 tasks 说明待建 |
| depends_on | 需求 id；不能自依赖或形成循环 |
| blocker | 阻碍和解除它所需的具体信息/操作 |

证据项包含 `path`（相对项目路径或已授权可读绝对路径）、`kind`（audit/human_review/contract/diagnostic）、`scope`（证据实际覆盖范围）。可选 `sha256` 固定证据字节，`check` 指定 JSON 点路径和期望值，例如：

```json
{"path":"experiments/example/audit.json","kind":"audit","scope":"完整本次数据的字节与读取一致性","check":{"field":"passed","equals":true}}
```

有 `check` 时检查器验证真实 JSON 字段；SHA变化不一定意味着结果失效，但会要求更新对应范围/版本再确认。无需对普通源码和所有文档普遍冻结 SHA。人工证据文件只记录已收到的反馈；检查器不能代替反馈。

verified 需求必须含义 confirmed、所有验收点 verified，且各点有可读取证据。未做项保持 pending；实验失败保留 failed；“部分通过”不变成“全部通过”。不明确的核心含义标 awaiting_user，而不是无期限继续调整实现。结构检查通过不代表所有需求通过。

## 任务与变更

任务至少连接一个 r 编号，列实际下一动作、影响的实现/数据、验证及停止条件。完成条件指向需求验收，不以“脚本写完”“实验 DONE”替代。

变更条目记录：日期、原始要求、新解释/修改、理由与证据、确认来源、影响需求、旧结果如何保留。仅核心语义/范围变化需要用户选择；普通实现修复无需增加审批。

迁移时保存旧文档，定位最新有效内容，避免把多个“最新状态”当成同等权威。观察事实变化更新证据快照；未获用户明确允许，不追改历史实验结果或删除已失败记录。
