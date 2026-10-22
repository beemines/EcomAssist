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

实施前另核对[huggingface_hub v2.2.0 snapshot_download](https://raw.githubusercontent.com/huggingface/huggingface_hub/v2.2.0/src/huggingface_hub/_snapshot_download.py)，源码SHA-256为`33aea763186df2d6600e2008e91ebb862cfc12907638caeab97e9865cf052d97`；支持`revision`、`local_dir`、`allow_patterns`、`token=False`，不使用已移除的`local_dir_use_symlinks`。上述Transformers锁定源码的`from_pretrained`支持`weights_only=True`、`local_files_only`、`use_safetensors`，底座从固定revision下载后离线安全加载，不执行远端代码。

GPU探测另按[PyTorch2.14 AMP文档](https://docs.pytorch.org/docs/2.14/amp.html)和[AdamW接口](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html)核对`torch.amp.GradScaler('cuda')`、autocast、unscale后裁剪与optimizer step；实际安装版本再核验，旧cuda.amp入口已弃用。独立ML锁文件SHA-256为`d8fc8a32b203781aae689f781c3f941b83b4e00bd01695be3c6beb5fbbff0da3`。

Task2按[SQLAlchemy2.0异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)核对独立短会话及execute/scalar，按[text绑定参数接口](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.text)使用命名参数，不拼接用户范围为SQL。业务锁定2.0.54；复用现有Database.session及3308隔离fixture，不新建第二个引擎生命周期框架。

Task3核对[Python3.13 sqlite3事务语义](https://docs.python.org/3.13/library/sqlite3.html#transaction-control-via-the-isolation-level-attribute)：显式BEGIN IMMEDIATE及参数绑定，连接上下文本身不负责关闭连接，需单独关闭；正常打开使用URI mode=rw，不能隐式新建丢失账本。[HTTPX AsyncClient/stream接口](https://www.python-httpx.org/api/#asyncclient)用于有界读取与显式关闭；主业务锁定httpx0.28.1，生产使用AsyncHTTPTransport(retries=0)、follow_redirects=False/trust_env=False，外层asyncio总时限120秒。智谱官方对话API确认max_tokens、thinking、reasoning_effort及usage三总数；无独立思考明细时保存NULL，不从字符数反推。完整completion作为全部输出计费，有明细仅核对其为子集，不额外重复相加。

Task9沿用已核对的SQLAlchemy2.0.54与ProcessingLease短事务/物理连接边界；另核对[MySQL命名锁官方说明](https://dev.mysql.com/doc/refman/8.4/en/locking-functions.html)中的连接所有权及释放语义，[SQLite UPSERT](https://sqlite.org/lang_upsert.html)中多列唯一冲突目标、excluded引用以及仅处理唯一约束的范围。MySQL locking-reads页面本次浏览返回不可用，不把该页面当已读取证据；实际FOR UPDATE与JOIN行为在3308独立schema真实测试。新增SQLite库仍显式BEGIN IMMEDIATE、FULL同步、显式关闭，错数据库身份/缺失/损坏回执拒绝当作空集合。

Task10实现前核对[MySQL JSON查询函数](https://dev.mysql.com/doc/refman/8.4/en/json-search-functions.html)的JSON_CONTAINS与数组包含语义、[FastAPI Query参数约束](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)，并沿用项目已锁FastAPI/Pydantic及现有ReviewRoute/guard_read。数据库DATETIME显示沿用既有后台的naive视为UTC口径，查询须显式时区后转换UTC半开范围；本章没有擅改原列或服务器时区，3308在范围端点实际验证。


Task6预备核对锁定Transformers5.20.2本机training_args.py、trainer.py、trainer_callback.py与BertTokenizer源码：training_arguments支持restore_callback_states_from_checkpoint；Trainer以严格np.greater更新最佳指标，平分不替换早期checkpoint；BertTokenizer当前构造参数为vocab（可为词表dict）。Windows训练锁按[Python3.12 msvcrt.locking官方接口](https://docs.python.org/3.12/library/msvcrt.html#msvcrt.locking)核对LK_NBLCK/LK_UNLCK及允许锁住文件末尾以外的字节，采用固定文件句柄锁，不按PID删除锁文件。早停、动态float多标签、processing_class、保存safetensors在明确tiny随机CPU连通脚本实际跑过；不据此声称HFL已训练或有分类成绩。


Task7核对本机锁定scikit-learn1.9.1的metrics/_classification.py中multilabel_confusion_matrix、f1_score、accuracy_score与hamming_loss签名和多标签分支，使用固定17列输入、zero_division=0；逐类零分母另外显式说明。固定三行矩阵对照已通过，空预测仍在分母内。阈值比较采用等价logit边界，避免对极端logit直接exp溢出；这只是数学/接口核验，不是实际模型评测。
