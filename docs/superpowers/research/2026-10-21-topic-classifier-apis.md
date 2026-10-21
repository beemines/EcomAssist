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

## 计划阶段：固定发布及源码签名（2026-10-21）

以下为公开注册元数据及官方源码只读核对，尚未安装/解析完整依赖，不能当作GPU运行成功：

| 组件 | 计划锁定版本 | 核对来源 |
| --- | --- | --- |
| Python | 3.12.13 | 本机已安装解释器清单 |
| torch CUDA | 2.14.1+cu130 | [官方CUDA130索引](https://download.pytorch.org/whl/cu130/torch/)，有cp312-cp312-win_amd64 wheel |
| transformers | 5.20.2 | [PyPI发布](https://pypi.org/project/transformers/5.20.2/)及官方v5.20.2源码 |
| accelerate | 1.15.0 | [PyPI版本元数据](https://pypi.org/pypi/accelerate/1.15.0/json) |
| numpy | 2.5.4 | [PyPI版本元数据](https://pypi.org/pypi/numpy/2.5.4/json)，有Windows cp312 wheel |
| scikit-learn | 1.9.1 | [PyPI版本元数据](https://pypi.org/pypi/scikit-learn/1.9.1/json)，有Windows cp312 wheel |
| iterative-stratification | 0.1.9 | [PyPI版本元数据](https://pypi.org/pypi/iterative-stratification/0.1.9/json)及原仓库0.1.9源码 |
| safetensors | 0.8.0 | [PyPI版本元数据](https://pypi.org/pypi/safetensors/0.8.0/json)，有Windows abi3 wheel |

torch Windows CUDA wheel SHA-256为`0a09031e93632d14ef49553acd6211ece3ae9cdc0969a369b8c24e3cc4d15be9`。PyPI默认wheel与该CUDA源wheel不是同一份，不能混用hash。[NVIDIA兼容说明](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)列CUDA13.x最低驱动580；本机610.88满足这个必要条件，但具体GPU内核仍需安装后实测。

HFL公开模型元数据返回revision `5c58d0b8ec1d9014354d691c538661bf00bfdb44`；文件列表包含pytorch_model.bin与tokenizer文件，不含原生safetensors。底座加载须使用当前torch安全weights-only能力，导出服务包转为safetensors，不能假设原仓库已有该格式。只读取了文件清单，没有下载权重。

| 官方固定源码 | SHA-256 | 已核对内容 |
| --- | --- | --- |
| [trainer.py](https://raw.githubusercontent.com/huggingface/transformers/v5.20.2/src/transformers/trainer.py) | `33ef308cf53cd54511823f05d8888eb25d6bd567c4ef0c777b51abd65306bbef` | constructor使用processing_class、compute_metrics、callbacks |
| [training_args.py](https://raw.githubusercontent.com/huggingface/transformers/v5.20.2/src/transformers/training_args.py) | `79f2569ffcb0fd842e5ca827bd180dfa2f02f5ace42f6c2906c2c289c8c0bd68` | eval_strategy；warmup_steps可为[0,1)比例，已无warmup_ratio字段 |
| [trainer_callback.py](https://raw.githubusercontent.com/huggingface/transformers/v5.20.2/src/transformers/trainer_callback.py) | `a9703b60f3d585627054ed976eca3dbea69fddcfd4eb01b1cc19bff67bccf00a` | early_stopping_patience/threshold和最佳checkpoint依赖 |
| [modeling_bert.py](https://raw.githubusercontent.com/huggingface/transformers/v5.20.2/src/transformers/models/bert/modeling_bert.py) | `fca25539f04aa121d000de218baedb619d744aaef7e93726e71ef555419c6a43` | BertForSequenceClassification的multi_label分支使用BCEWithLogitsLoss |
| [modeling_utils.py](https://raw.githubusercontent.com/huggingface/transformers/v5.20.2/src/transformers/modeling_utils.py) | `553412f58334f65abba617f3b344828698dbf63615e109159fd03dafd3422d38` | save_pretrained无显式safe_serialization参数，实施时核验实际safetensors文件而不盲传旧参数 |
| [ml_stratifiers.py](https://raw.githubusercontent.com/trent-b/iterative-stratification/0.1.9/iterstrat/ml_stratifiers.py) | `5bdfa0db803e006884e2d228c2a97377e438b5ad9a0f24891fe77f2c53f54bf3` | MultilabelStratifiedShuffleSplit及固定random_state |

[FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/)用于加载一次服务模型及释放资源；[HTTPX超时](https://www.python-httpx.org/advanced/timeouts/)分连接/读/写/连接池，read timeout不是整次操作总时限，旁路调用还须外层总超时。
