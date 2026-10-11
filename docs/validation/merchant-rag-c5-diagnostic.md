# C5/dense 单次实际诊断

用户明确授权及root Ruling21后执行一次，不替代固定试跑或全量资格。

- Probe：`5e6b712636684cd1bd3c5ec469192050`；原新低思考pilot：`201215b02b874feea7e866db10ee23db`。
- 真实合法结束：`stop`，回答158字，严格引用/完整性校验通过；耗时4.645734999794513秒。
- 实际请求：answer=1；rewrite/self_check/judge/embedding/rerank/Milvus均0；cleanup成功，errors/unverified均空。
- 固定GLM-5.3-Flash/low、回答512、retry0、SDK60秒/chat240秒。配置指纹`191d53c027323fa8005327336e6ec0e737f7d196eebd6ad05f2dea7258f60913`保持。
- 离线输入估算5726/8000；10引用逐值相等，actual来源映射/冻结语料/prompt hash相等，generation无gold。
- 生产源码`cfc65fdb99e44de68c2727e05743a384bba6e89e`；私有正文、流事件及完整请求仅ignored cache保存。

原失败finish/具体ServiceError.code未捕获；本次成功不能说明旧失败根因。原完整消息字节未保存，验证是同production builder/证据/prompt/config一致。原两次实际pilot、两探针公开文件均保留，不补行或覆盖。
