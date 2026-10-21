# 第十步官方接口与环境核对（设计阶段）

日期：2026-10-21。用户批准本章在Context7不可调用时，以官方文档与锁定版本源码核对接口；该批准不更换技术选型。

## 已读来源与设计约束

1. [HFL官方模型卡](https://huggingface.co/hfl/chinese-roberta-wwm-ext)与[官方配置](https://huggingface.co/hfl/chinese-roberta-wwm-ext/raw/main/config.json)：固定模型ID为hfl/chinese-roberta-wwm-ext；配置model_type=bert、12层、hidden_size768、最大位置512。模型卡明确须使用Bert相关加载函数；不能因为名称含RoBERTa就强制实例化另一个RoBERTa架构。后续用对应Auto类加载该模型并加多标签分类头，全参数训练，不替换底座。
2. [Transformers BERT文档](https://huggingface.co/docs/transformers/en/model_doc/bert)及[Trainer接口](https://huggingface.co/docs/transformers/en/main_classes/trainer)：核对多标签分类、训练/验证数据和compute_metrics、callbacks、processing_class及训练参数入口。当前在线文档为滚动版本；实施前须对拟锁版本的源码再核对参数名，不直接复制main分支API。
3. [PyTorch官方本地安装说明](https://pytorch.org/get-started/locally/)：Windows/NVIDIA使用相匹配的CUDA wheel；先核验具体发布版本、Python/wheel/驱动兼容性。网页部分静态选择器与页面其他版本信息不完全一致，不据此宣称某一数字是当前最新稳定版本。本阶段没有安装训练依赖。
4. [SQLAlchemy官方2.0异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)及仓库锁定2.0.54的app/db/session.py：沿用现有Database/短会话边界，只读SELECT统计现有问题池，未执行建表、清理或写回。
5. [Transformers早停回调](https://huggingface.co/docs/transformers/en/main_classes/callback)：EarlyStoppingCallback依赖load_best_model_at_end，验证与保存节奏须一致。BERT多标签文档示例使用problem_type=multi_label_classification、sigmoid及float标签，不使用softmax。设计采用验证选最佳、随后验证选阈值，测试不参与。
6. [scikit-learn原文](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.multilabel_confusion_matrix.html)：类级输出形状为(n_labels,2,2)，顺序为TN/FP/FN/TP；本章固定17列顺序，缺类仍报告支持数。[iterative-stratification原项目](https://github.com/trent-b/iterative-stratification)提供多标签分层基础，普通单标签stratify不能直接替代；小批训练约束及group_id需外围实现，不能声称原库本身支持组约束。
7. [智谱模型页](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash)、[核心参数](https://docs.bigmodel.cn/cn/guide/start/concept-param)、[对话接口](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)及[价格](https://docs.bigmodel.cn/cn/guide/start/pricing)：5.3 Flash强制thinking，支持low/high/max，最大输出131072；标准价格未缓存输入0.8、输出2.8元/百万token。预算设计采用最大窗口及输出先预留，完整usage可核对再结算，未知保持预留；不把字符估算当硬计费上限。教师采用low，不改第九步线上配置。

## 本机与语料只读结果

- 当前主环境Python3.13.5；torch、transformers、datasets、sklearn、onnxruntime、onnx、iterstrat未安装。
- 使用工作区专用uv缓存做已安装解释器只读清单，确认已有Python3.12.13和3.11.15等解释器；尚未选择训练依赖版本或创建环境，不需要为探测下载解释器。
- GPU：NVIDIA GeForce RTX4060 Laptop，显存8188MiB，检查时空闲7065MiB，驱动610.88。物理内存34024747008字节，约31.7GiB。D盘空闲162795048960字节。
- 本机3307/customer_service问题池29行，按BINARY TRIM(raw_question)精确去重21问，ID范围1–31；来源retrieval_low_conf25、self_check1、user_feedback3。均长21.3字、最大58字。
- 13行匹配CH09/验收/模拟/测试关键词，仅是来源核查线索，不等同于严格真伪判定。不能把全部池记录标成真实客户数据或当作17类均有覆盖。没有导出或外发原话。

## 后续验证边界

模型权重revision、训练依赖的确切版本和wheel、混合精度/早停/多标签损失、分组多标签分层抽样、逐类2×2混淆矩阵及服务接口，进入书面设计与计划时继续核对。实现前不安装、不下载权重、不运行训练；不能用模拟日志、随机权重或关键词规则冒充全参微调的实际成绩。
