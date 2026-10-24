# 文档导航

新读者从[首次部署](getting-started.md)开始，开发者看[架构](architecture.md)与[测试](development.md)。当前主题模型的可移植操作见[主题分类器指南](topic-classifier.md)。

## 按任务查找

| 任务 | 文档 |
| --- | --- |
| 先看所有页面与主要页签 | [全页面演示视频与章节](demo-video.md) |
| 安装、数据库、知识库、启动 | [首次部署](getting-started.md) |
| 理解在线与离线链路 | [系统架构](architecture.md) |
| 跑测试或提交修改 | [开发与测试](development.md)、[贡献指南](../CONTRIBUTING.md) |
| 运行 MCP 工具演示 | [工具系统](tool-system-demo.md)、[第八步手动验收](ch08-manual-acceptance.md) |
| 本地 Langfuse 与数据飞轮 | [第九步演示](ch09-local-demo.md)、[手动验收](ch09-manual-acceptance.md) |
| 训练与部署主题模型 | [主题分类器](topic-classifier.md)、[第十步本机手册](ch10-pycharm-acceptance.md) |
| 查看 RAG 实验结果 | [300题结果分析](validation/merchant-rag-comparison-analysis.md) |
| 查看第十步真实结果 | [交付报告](superpowers/reports/2026-10-21-ch10-delivery.md)、[最终在线验证](superpowers/reports/2026-10-23-ch10-closeout-verification.md) |
| 查集成与推送记录 | [第十步集成](superpowers/reports/2026-10-24-ch10-integration.md) |

## 十章路线

| 阶段 | 主题 | 过程记录 |
| --- | --- | --- |
| 01 | 流式多轮对话与售后信息抽取 | [ch01](../dev-notes/ch01.md) |
| 02 | 工具调用与持久化 | [ch02](../dev-notes/ch02.md) |
| 03 | 知识入库、切分与向量化恢复 | [ch03](../dev-notes/ch03.md) |
| 04 | 混合检索、重排与生成质量 | [ch04](../dev-notes/ch04.md) |
| 05 | Workflow 与受控 Agent | [ch05](../dev-notes/ch05.md) |
| 06 | 意图理解、订单选择与退款申请 | [ch06](../dev-notes/ch06.md) |
| 07 | 分层上下文与长对话 | [ch07](../dev-notes/ch07.md) |
| 08 | 可插拔工具、MCP 与审计 | [ch08](../dev-notes/ch08.md) |
| 09 | Langfuse、成本与数据飞轮 | [ch09](../dev-notes/ch09.md) |
| 10 | 多标签主题分类器 | [ch10](../dev-notes/ch10.md) |

## 文档分工

- [`prompts/`](prompts/)保存用户原始提示词与DDL，需求原文和后续实现补充分别记录。
- [`superpowers/specs/`](superpowers/specs/)是设计，[`superpowers/plans/`](superpowers/plans/)是执行计划。
- [`superpowers/research/`](superpowers/research/)记录文档与锁定版本接口核对。
- [`superpowers/reports/`](superpowers/reports/)和[`validation/`](validation/)保存审查、实验、故障与验收结论。
- [`dev-notes/`](../dev-notes/)按阶段追加用户原话、产出、纠偏、失败与返工。

章节手册包含带日期的本机路径、端口与历史操作。复现当前功能时优先使用通用指南和手册顶部的最新状态；历史“未训练”“未发布”描述保留其时间含义。原始语料、模型权重、预算账本和私有回执未随仓库发布。
