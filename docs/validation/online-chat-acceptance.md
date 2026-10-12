# 在线客服聊天修复验收

验收日期：2026-10-12。用户授权：修复后用浏览器验收，通过后提交、合入 master 并推送；Computer Use 无法启动后，明确允许真实 Chromium 自动化替代。

## 修复结果

在线聊天原来仍使用旧 84 块 XM 合成资料，而商家评估使用另一份 50 块资料。本次将冻结八文档的 50 块发布到独立 `knowledge_merchant_live`，MySQL 保留旧资料和会话。为这份语料独立做八题检索校准；阈值不是业务置信度概率，也不代表全体问题的生成质量。

修复合法 FAQ 申请被模型同义改写后触发原文片段守卫的问题：只在可信聊天边界归一合法参数，检索仍读取完整用户原话。无效改写结构显式使用原话降级，严格解析、鉴权、取消、超时和数据库错误守卫保持。在线低思考配置可选，不影响评估模型参数；回答 512、改写/自评 2048、期限和零重试保持。

## 实际浏览器案例

| 用户问题 | 期望及实际通过的要点 | 完整回复耗时 |
| --- | --- | --- |
| 给大猫用的那款猫砂盆能装多少砂 | MH-LP200，12L；引用打开对应章节 | 18.665 秒 |
| MH-W40 水箱多大，有杀菌功能吗？ | 4L、UV 紫外杀菌；型号来源正确 | 22.719 秒 |
| 普通地区买80元商品，邮费多少？ | 10元；满99元包邮；来源可查看 | 13.245 秒 |
| 如何申请退款，钱退到哪里？ | 我的订单申请退款、原路退回；未承诺到账天数 | 17.521 秒 |
| 你们提供宠物洗澡美容服务吗，具体价格是多少？ | 明确资料不足拒答，无编造引用；原话入池 | 10.38 秒 |

四个知识回答都正常结束、多帧 SSE 输出、可见增量渲染，并能打开引用原文。赞/踩点亮、显示已反馈并一次锁定；按既有设计仅存前端状态。五轮四角色消息、有效工具参数与结果、最终回复主键/正文均通过只读数据库核验。

RAG 页面独立只读验收通过：真实 20 个柱子、Recall 指标切换、质量策略切换及环形图正常；1188 完成、12 条历史错误及共同样本范围仍清楚显示。没有重跑 300 题。首次 RAG 等待在并行完整测试期间超过 15 秒，失败记录保留；独立复测加载 3.301 秒通过。

## 测试与评审

- 默认完整回归：`python -m pytest -q --tb=short`，**1531 passed、116 skipped、0 failed**，退出码 0。116 项按既有默认集成开关跳过，未把跳过项算成成功。
- 普通超时取消分类修复专项：383 passed、2 skipped；默认模型工厂兼容性返工专项：140 passed。
- 任务复审：三个发现全部解决；最终代码复审无 Critical、Important 或待处理 Minor。
- 全套首次 15 个失败全部为默认工厂额外传 None 参数，已保留 RED 后仅修默认调用形状；没有批量修改既有 fake。

## 留证及演示

- [综合浏览器结果](online-chat-acceptance.json)、[截图](images/online-chat-acceptance/large-cat.png)、[原文弹窗](images/online-chat-acceptance/large-cat-source.png)。
- [RAG 图表结果](online-rag-page-acceptance.json)、[图表截图](images/online-chat-acceptance/rag-evaluation.png)。
- [实际消息与拒答池核验](online-chat-storage-proof.json)、[50 块发布范围](online-merchant-publication.json)、[八题原始校准](online-merchant-calibration.json)。
- [最终测试记录](online-chat-test-results.json)、[代码评审](online-chat-review.md)、[阶段留痕](../../dev-notes/ch04.md)。
- [首次关键词失败](online-chat-acceptance-first-failure.json)、[原 RAG 等待失败](online-chat-acceptance-rag-wait-failure.json)保留，不改写成成功。

本机聊天页：<http://127.0.0.1:8001/>；RAG 页面：<http://127.0.0.1:8001/rag-eval>。

```powershell
uv run --locked uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8001 --workers 1
```

启动和 curl 的完整演示命令见 [README](../../README.md)。密钥、运行日志、本地配置和备份均保持 Git 忽略。

## 执行决定

1. 复用用户已有的合并/推送授权，不重复请求设计或发布批准；若授权范围误读，代价是回退本地配置或提交。
2. 浏览器和测试通过前不提交，优先于技能默认逐任务提交；代价是验证期间修改暂存于本地工作树。
3. FAQ 参数归一只在可信聊天边界执行，直接工具和仓储守卫保持；若实现错误，代价是参数审计不一致或条件丢失，因此专项和实际流水都核验了完整原话及有效申请。

正在服务的工作树、本地配置和缓存保留，避免合并后的清理影响页面运行。
