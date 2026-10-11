# 本轮真实改写观测边界

Run `7d421bf017ff4c02afec385178848fde`；方法SHA `0f12595c000e8c84bcfa7f0182b2b2350fc5e04dd491504b1122400e8474cd8c`，独立旁路元数据不补入质量记录。原请求、返回对象、严格校验与期限不变；只私存正文，本报告仅类型/结束状态/长度/schema形状。真实rewrite10，与生产计数一致、观测错误0。

| 题号 | HTTP / finish | 原JSON形状 | LC parsed / parsing_error | 生产结果 |
|---|---|---|---|---|
| A21 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 2, "item_shapes": [{"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| A43 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 2, "item_shapes": [{"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| B3 | 200 / stop | {"type": "list", "length": 2, "item_shapes": [{"type": "dict", "fields": {"answer": {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list"}}}}}, {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 1}}}]} | NoneType / OutputParserException | invalid_structured_output |
| B54 | 200 / stop | {"type": "dict", "fields": {"answer": {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 3}}}}} | NoneType / OutputParserException | invalid_structured_output |
| C35 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 2, "item_shapes": [{"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| C5 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 2, "item_shapes": [{"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| D1 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 3, "item_shapes": [{"type": "str"}, {"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| D3 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 2, "item_shapes": [{"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| E19 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 3, "item_shapes": [{"type": "str"}, {"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |
| E2 | 200 / stop | {"type": "dict", "fields": {"standard": {"type": "str"}, "expansions": {"type": "list", "length": 3, "item_shapes": [{"type": "str"}, {"type": "str"}, {"type": "str"}]}}} | QueryPlan / None | legal |

B3/B54各一次共享改写失败，分别投影四策略，共8个rewrite_error；不是8次改写请求。HTTP200和finish=stop不能代替结构合法性。两题原消息hash与离线固定输入相等，low/2048/json_object/nonstream未变；原解析错误和生产invalid_structured_output保留，不转换为成功。原失败的具体正文/finish/code未捕获，不能反推旧根因。

当前40attempted/32completed/8rewrite_error、清理成功；实际matching_pilot=false，full未运行，收费停止。所有原质量报告字节保持，不重新生成、不加独立probe/第二pilot/参数修正。

完整安全元数据见[JSON](merchant-rag-observed-rewrite-evidence.json)，真实质量记录见[本轮原JSON](merchant-rag-observed-pilot.json)。
