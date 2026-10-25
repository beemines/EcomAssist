# 全页面演示

[![2 分 11 秒完整动态导览：点击下载MP4](assets/pages-walkthrough.gif)](https://github.com/beemines/EcomAssist/raw/refs/heads/master/docs/assets/pages-walkthrough.mp4)

[下载 MP4](https://github.com/beemines/EcomAssist/raw/refs/heads/master/docs/assets/pages-walkthrough.mp4) · [仓库内视频](assets/pages-walkthrough.mp4) · [静态封面](assets/pages-walkthrough-poster.jpg) · [返回项目](../README.md)

这是 **2026-10-24** 当前版本实际页面画面剪辑的无声导览，包含中文说明字幕。视频为 H.264 / MP4、1600 × 900、24 fps，长 **2 分 11 秒**，内含章节；不支持网页预览的 Markdown 阅读器可下载后播放。

GitHub的仓库MP4文件页不内嵌播放器，因此README使用包含全部31个镜头、同样时长的动态GIF展示，MP4提供下载。离线打开仓库内MP4可使用播放器暂停、拖动和按章节查看。

## 章节

时间对应视频进度条；下面覆盖七个主页面、主要页签和三个样本审核页。`/review-queue` 是飞轮待审的同页别名，Langfuse 是后台链接到的独立应用。

| 时间 | 页面 | 展示内容 |
| --- | --- | --- |
| 00:00 | `/admin` | 后台统一入口 |
| 00:05 | `/` | 聊天主界面、常见问题填入、已保存的演示问答 |
| 00:17 | `/review` | 待审状态筛选与空队列 |
| 00:21 | `/observability` | 意图成本、评估趋势、置信度三个页签 |
| 00:31 | `/rag-eval` | 已保存的300题报告、四策略图、回答质量、逐题筛选栏 |
| 00:48 | `/topics` | 当前批次统计与17类主题条形图 |
| 01:00 | `/topics/acceptance` | 总览、流程记录 |
| 01:09 | `/topics/acceptance#evaluation` | 评测范围、各类P/R/F1、混淆矩阵、验证阈值、多标签示例 |
| 01:32 | `/topics/acceptance#data` | 语料血缘、全参数训练、独立部署、产物清单 |
| 01:50 | `/topics/acceptance#errors` | 复核来源、结果与错误分布 |
| 01:59 | `/topics/pilot-review` | 64条合成训练对照的已保存人工审核界面 |
| 02:03 | `/topics/test-review` | 68条合成测试题的已保存AI代审界面 |
| 02:07 | `/topics/error-review` | 34条合成错例的已保存AI代审界面 |

主应用使用本机8007演示配置；最后三个审核镜头使用8010的本轮冻结复核包。首次克隆后按[快速开始](getting-started.md)部署自己的配置；私有模型、原始问题与回执不随仓库发布。

## 画面与数据说明

- 保留项目现有绿色界面。视频新增的是章节标题与字幕，没有为展示更改页面、指标或后台数据。
- 聊天历史整栏裁掉，主题页仅显示统计与左侧图表，RAG逐题页仅显示筛选区。待审原话和检索快照详情未展开；所有样本审核镜头均来自已核实的合成题包。
- 当前演示配置的Langfuse成本统计不可用、评估趋势服务不可用、置信度报告缺失，视频如实保留这些状态。配置与验收方法见[第九步演示](ch09-local-demo.md)。本视频没有展示独立Langfuse的完整trace树。
- RAG图表使用已保存的300题合并结果；分类器显示完整187条银标测试的Macro-F1 **0.7672**、Micro-F1 **0.7606**。固定诊断8/8与总体质量分别展示，详见[主题分类器指南](topic-classifier.md)。
- 本次只浏览页面与已有记录，没有发送聊天请求、训练、重跑收费评估、提交人工审核、发布知识或执行业务申请。视频用于了解界面，完整功能验收仍以各步骤报告和复现命令为准。

源码与本仓库制作的演示媒体采用[MIT License](../LICENSE)；第三方模型、数据及依赖的授权以各自项目为准。
