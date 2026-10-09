# RAG 评估知识材料草稿

这批资料用于项目演示与四策略评估，不代表真实商家制度。四篇原始资料来自用户本次提供的正文；另外四篇由用户授权“你自己编写一下”后补充。补充部分须与评估集一起确认、冻结后再建库。本目录尚未导入正在提供聊天服务的业务库。

| 文件 | 来源 | 内容类型 |
| --- | --- | --- |
| after-sales-manual.md | 用户提供，恢复 Markdown 标题换行 | manual |
| product-faq.md | 用户提供，恢复 Markdown 标题换行 | faq |
| product-specs.md | 用户提供 | manual |
| returns-policy.md | 用户提供，恢复 Markdown 标题换行 | policy |
| membership-benefits.md | 经授权补写的演示规则 | policy |
| integral-rules.md | 经授权补写的演示规则 | policy |
| invoice-policy.md | 经授权补写的演示规则 | policy |
| cat-bed-care.md | 经授权补写的演示规则 | manual |

建库只选择上述八篇，README 不作为业务知识入库。原来的 XM 型号语料、8 元运费和两个工作日发货属于另一版合成资料，不能混入本批评估。实际块数取决于原始文本及切分配置，不预设为 51 或 52。

2026-10-09 离线预检：八篇均能以 UTF-8 严格解码。使用现有结构切分器，target_chars=1200、overlap_chars=120，分别产生 7/14/13/9/2/2/2/1 块，共 50 块。这只是切分结果，尚未向量化或导入 MySQL/Milvus。

会员等级沿用原 FAQ 的累计消费口径，按有效累计消费金额而非年消费确定；与此冲突的年消费题应保留原始版本和修订记录。新增纸质专票资料后，原 D3 不再是库外问题。原始 300 题不能未经审标直接当作可靠金标，具体待修订项见 docs/validation/rag-evaluation-materials-audit.md。
