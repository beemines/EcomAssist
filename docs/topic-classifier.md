# 17类多标签主题分类器

本模块给低置信度问题池做离线批量归类，帮助判断先补哪些知识。它使用HFL `chinese-roberta-wwm-ext` **全参数微调**，没有LoRA，也不微调embedding或在线意图模型。

## 数据与标签

权威定义来自[`config/topic-taxonomy.json`](../config/topic-taxonomy.json)：退换货、物流、尺码、发票、质量问题、运费、优惠活动、价保、支付、订单修改、库存补货、商品信息、保修维修、账号、会员积分、评价、其他。

一句只标实际肯定的诉求；多个诉求可多选。“买大了想退”包含尺码与退换货，“不要退，只想修”只对应保修维修。“其他”与前16类互斥；业务标签全未过线进入`needs_review`，不靠argmax伪造有把握的标签。

处理流程为：只读快照与脱敏 → 术语统一/教师预标 → 实际人审 → 同义家族分组及约80/10/10分层 → 仅训练集增强 → 全参训练 → 验证选模及阈值 → 留出测试和错例复核 → 导出。

验证与测试不接受训练增强。已看过的测试错例不回流本轮训练或重新选阈值。AI代审和真实人工回执使用不同来源，不把委托AI判断当作用户逐条核对。

## 独立环境

```powershell
uv sync --project ml/topic_classifier --locked
uv run --project ml/topic_classifier --locked python -m ml.topic_classifier.cli --help
uv run --locked python -m app.topics.cli --help
uv run --locked python -m app.topics.data_cli --help
```

业务环境不导入训练库。训练环境的固定依赖见[pyproject](../ml/topic_classifier/pyproject.toml)和[锁文件](../ml/topic_classifier/uv.lock)。本仓库不分发私有训练语料、模型权重或原开发机的人审回执。

## 使用自己准备的模型包

先用自己的有来源数据与审核流程完成训练、评测和导出。CLI分别提供`split`、`freeze-augmentation`、`train`、`evaluate`、`finalize`和`serve`；逐项参数以`--help`为准，受控历史修复命令不属于首次训练必跑步骤。教师预标与合成数据阶段可能付费，并应使用持久预算；不要删除账本重置累计费用。

通过导出/发布契约的本地模型包准备好后，可从仓库根目录启动：

```powershell
uv run --project ml/topic_classifier --locked python -m ml.topic_classifier.cli serve --bundle .cache/my-topic-model --host 127.0.0.1 --port 8103
curl.exe http://127.0.0.1:8103/health
```

`.cache/my-topic-model`是你实际准备的模型包目录，占位路径本身不包含可用权重。服务仅加载本地文件，验证权重、清单、术语与证据；不在启动时下载或访问数据库。当前实现是Transformers CPU服务，没有ONNX导出步骤。

## 旁路批次

私有profile严格只包含三个字段；相对路径以profile所在目录解析：

```json
{
  "service_url": "http://127.0.0.1:8103",
  "manifest_path": "my-topic-model/manifest.json",
  "runtime_root": "my-topic-runtime"
}
```

例如保存在`.cache/topic-profile.json`，在[显式迁移](getting-started.md)完成后先预览：

```powershell
uv run --locked python -m app.topics.cli verify --database configured
uv run --locked python -m app.topics.cli preview --database configured --profile .cache/topic-profile.json --from-id 1 --to-id 100 --limit 100 --output .cache/topic-preview.json
uv run --locked python -m app.topics.cli run-once --database configured --profile .cache/topic-profile.json --preview-file .cache/topic-preview.json
```

先核对实际ID边界、模型与目标库。最后一行默认dry-run，显式加`--execute`才调用本地分类器并写`topic_classifications`。同一预览重放不重复插入；更换模型、原文改变或身份不匹配会阻止错误覆盖。持续批量处理用`watch`，默认也为dry-run，执行方式与故障暂停详见CLI帮助及[本机手册](ch10-pycharm-acceptance.md)。

## 后台与现有演示

`/topics`按当前模型统计，显示未有效归类数量、17类分布、来源/时间筛选和原话明细；`/topics/acceptance`显示已保存的评测证据。当前演示工厂的`CH10_ENV_FILE`显式选择应用配置，`CH10_TOPIC_PROFILE`选择模型profile，`CH10_REVIEW_ROOT`选择允许的复核批次根。需要沿用原开发机材料时，按[PyCharm手册顶部配置](ch10-pycharm-acceptance.md)运行8007/8010/8103。

现有第5次训练的187条合成银标Macro-F1为0.7672、Micro-F1为0.7606；8条固定诊断通过，20条实际池记录归类与幂等重放完成。原池真实性未核实，最终102条测试/错例由用户授权AI代审，且存在一对历史训练/验证近重复。这是有边界的功能演示，完整结果、分母与限制见[交付报告](superpowers/reports/2026-10-21-ch10-delivery.md)和[后端审查处置](superpowers/reports/2026-10-23-ch10-backend-review.md)。
