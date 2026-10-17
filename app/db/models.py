# SQLAlchemy 映射业务、知识和质量表，实际建表以 sql 目录中的 DDL 为准。
from datetime import datetime
from typing import Any

from sqlalchemy import FetchedValue, ForeignKey, Index, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, ENUM, INTEGER, JSON, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """只映射已有表；建表始终由用户提供的 sql/schema.sql 执行。"""


# 会话主表保存用户归属、生命周期状态及数据库生成的时间。
class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("idx_user_id", "user_id"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "客服会话"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="会话主键")
    user_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment="用户标识")
    status: Mapped[str] = mapped_column(ENUM("进行中", "已转人工", "已结束"), nullable=False, server_default=text("'进行中'"), comment="处理状态")
    summary: Mapped[str | None] = mapped_column(TEXT, nullable=True, comment='最近几段梗概拼成的投影,拼装时跟证据一起挂在用户那句之后')
    summary_upto_msg_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), nullable=True, comment='摘要已覆盖到哪条消息,滑窗从其后接原文')
    layer1_from_msg_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), nullable=True, comment='层1(原文)起点;此 id 之后原样,之前渲染成半压形态')
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="开启时间")
    updated_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), server_onupdate=FetchedValue(), comment="更新时间")


# 消息流水保留工具申请和结果关联标识，支撑审计与完整轮次回放。
class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (Index("idx_conversation_id", "conversation_id"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "会话消息流水"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="消息主键")
    conversation_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey("conversations.id", name="fk_messages_conversation"), nullable=False, comment="所属会话")
    role: Mapped[str] = mapped_column(ENUM("user", "assistant", "tool"), nullable=False, comment="角色:用户/助手/工具结果")
    content: Mapped[str | None] = mapped_column(TEXT, nullable=True, comment="消息正文,assistant 纯工具调用时可为空")
    tool_calls: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON(none_as_null=True), nullable=True, comment="assistant 消息带的工具调用申请单")
    tool_call_id: Mapped[str | None] = mapped_column(VARCHAR(64), nullable=True, comment="tool 消息对应的申请单 id,回灌时对号入座")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="产生时间")


class ConversationSummary(Base):
    """用户DDL的追加式摘要段；不新增原DDL未定义的外键或索引。"""
    __tablename__ = 'conversation_summaries'
    __table_args__ = (Index('uk_conv_seq', 'conversation_id', 'seq', unique=True),
        Index('idx_conv_upto', 'conversation_id', 'upto_msg_id'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '分段摘要,一段一行只追加'})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False)
    seq: Mapped[int] = mapped_column(INTEGER, nullable=False, comment='第几段,从 1 开始')
    from_msg_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False, comment='这段覆盖的消息区间,闭区间')
    upto_msg_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False)
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'))


# 映射既有 FAQ 表的原始问答与分类字段。
class FAQ(Base):
    __tablename__ = "faq"
    __table_args__ = (Index("idx_category", "category"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "常见问答"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="FAQ 主键")
    question: Mapped[str] = mapped_column(VARCHAR(512), nullable=False, comment="问题")
    answer: Mapped[str] = mapped_column(TEXT, nullable=False, comment="答案")
    category: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment="分类")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), server_onupdate=FetchedValue(), comment="更新时间")


# 人工工单使用稳定业务编号作为主键，与会话关联供追溯。
class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (Index("idx_conversation_id", "conversation_id"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "人工工单"})

    ticket_no: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True, comment="工单号,如 T20260701008")
    conversation_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey("conversations.id", name="fk_tickets_conversation"), nullable=False, comment="关联会话,可倒查当时聊了什么")
    description: Mapped[str] = mapped_column(TEXT, nullable=False, comment="问题描述")
    ticket_type: Mapped[str] = mapped_column(ENUM("售后", "投诉", "咨询"), nullable=False, comment="工单类型")
    status: Mapped[str] = mapped_column(ENUM("待处理", "已处理"), nullable=False, server_default=text("'待处理'"), comment="处理状态")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")


class RefundRequest(Base):
    """只映射显式提交的待审核申请，不开放修改或支付动作。"""
    __tablename__ = 'refund_requests'
    __table_args__ = (Index('uk_refund_request', 'request_no', unique=True),
        Index('uk_refund_offer', 'offer_id', unique=True), Index('uk_refund_pending', 'pending_key', unique=True),
        Index('idx_refund_owner_order_status', 'user_id', 'order_id', 'status'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '用户显式提交的待审核退款申请'})
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment='申请主键')
    request_no: Mapped[str] = mapped_column(VARCHAR(65), nullable=False, comment='服务器稳定申请号')
    conversation_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('conversations.id', name='fk_refund_conversation'), nullable=False, comment='来源会话')
    user_message_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('messages.id', name='fk_refund_user'), nullable=False, comment='本轮用户消息')
    assistant_message_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('messages.id', name='fk_refund_assistant'), nullable=False, comment='已完成助手答复')
    checkpoint_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False, comment='不可变完成根检查点')
    offer_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment='服务器申请许可')
    user_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment='可信用户身份')
    order_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment='可信订单身份')
    pending_key: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment='用户订单规范JSON数组的SHA256')
    reason: Mapped[str] = mapped_column(ENUM('unwanted', 'quality', 'not_as_described', 'wrong_or_missing', 'damaged', 'other'), nullable=False, comment='用户表单原因')
    amount_cents: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False, comment='订单实付整数分')
    currency: Mapped[str] = mapped_column(ENUM('CNY'), nullable=False, comment='订单币种')
    status: Mapped[str] = mapped_column(ENUM('待审核'), nullable=False, server_default=text("'待审核'"), comment='待审核申请状态')
    order_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, comment='原订单事实完整快照')
    policy_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, comment='原政策证据全文与路径快照')
    decision_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, comment='原模型判断及说明快照')
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='服务器提交时间')


# 知识分块原文及向量化状态由 MySQL 保存，主键与向量索引对应。
class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (Index("idx_category", "category"), Index("idx_vectorize_status", "vectorize_status"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "知识库 chunk 原文权威源"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="chunk 主键,与 Milvus 集合主键对齐")
    category: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, comment="分类 / 上级标题路径,进向量化文本")
    questions: Mapped[str] = mapped_column(TEXT, nullable=False, comment="问法或本节标题,多个问法换行分隔,进向量化文本")
    answer: Mapped[str] = mapped_column(TEXT, nullable=False, comment="正文答案,进向量化文本")
    section_path: Mapped[str | None] = mapped_column(VARCHAR(512), nullable=True, comment="章节路径,元数据,溯源用,不进向量")
    content_type: Mapped[str | None] = mapped_column(VARCHAR(32), nullable=True, comment="内容类型:faq / policy / manual 等,元数据")
    is_key_clause: Mapped[bool] = mapped_column(TINYINT(display_width=1), nullable=False, server_default=text("0"), comment="是否关键条款,0 否 1 是,元数据")
    prev_chunk_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), ForeignKey("knowledge_chunks.id", name="fk_chunks_prev", ondelete="SET NULL"), nullable=True, comment="前一块指针,元数据")
    next_chunk_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), ForeignKey("knowledge_chunks.id", name="fk_chunks_next", ondelete="SET NULL"), nullable=True, comment="后一块指针,元数据")
    vector_id: Mapped[str | None] = mapped_column(VARCHAR(64), nullable=True, comment="Milvus 集合 knowledge 里的主键,写入后回填")
    vectorize_status: Mapped[str] = mapped_column(ENUM("pending", "done"), nullable=False, server_default=text("'pending'"), comment="待向量化 / 已向量化,双写幂等靠它")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), server_onupdate=FetchedValue(), comment="更新时间")


# 离线 QA 暂存表保留批次、来源和去重决策，便于重放及追溯。
class QAExtractionStaging(Base):
    __tablename__ = "qa_extraction_staging"
    __table_args__ = (Index("idx_batch_no", "batch_no"), Index("idx_status", "status"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "历史对话抽 QA 的离线中转暂存表:分批抽取、整体去重,保留项入 knowledge_chunks,建库完成可清空"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="暂存行主键")
    batch_no: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment="抽取批次号,一批几十个会话跑一次,分批防串味、按批追溯")
    source_ref: Mapped[str | None] = mapped_column(VARCHAR(255), nullable=True, comment="来源会话 / 导出文件标识,溯源用,不入最终知识库")
    question: Mapped[str] = mapped_column(TEXT, nullable=False, comment="LLM 从会话抽出的用户问法")
    answer: Mapped[str] = mapped_column(TEXT, nullable=False, comment="LLM 从会话抽出的客服答案")
    status: Mapped[str] = mapped_column(ENUM("extracted", "kept", "discarded"), nullable=False, server_default=text("'extracted'"), comment="已抽出待去重 / 去重保留 / 去重丢弃")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")


# 低置信度池保留拒答原话和来源，useful 只参与生成判定、不落字段。
class LowConfidenceQuestion(Base):
    __tablename__ = "low_confidence_questions"
    __table_args__ = (Index("idx_source", "source"), Index("idx_created_at", "created_at"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "低置信度问题池"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    conversation_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), ForeignKey("conversations.id", name="fk_lcq_conversation"), nullable=True, comment="来源会话")
    raw_question: Mapped[str] = mapped_column(TEXT, nullable=False, comment="用户原话,带情绪口语")
    source: Mapped[str] = mapped_column(ENUM("retrieval_low_conf", "self_check", "user_feedback"), nullable=False, comment="入池入口:检索证据低 / 生成自评不足 / 用户反馈未解决")
    reason: Mapped[str | None] = mapped_column(TEXT, nullable=True, comment="判不能的原因,留作复盘")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="入池时间")


# 忠实度个案一题一行，累计复发次数并保留证据全集及最近处置时间。
class FaithCase(Base):
    __tablename__ = "faith_cases"
    __table_args__ = (Index("uk_eval_id", "eval_id", unique=True), Index("idx_status", "status"), Index("idx_last_seen_at", "last_seen_at"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "ch04 忠实度编造个案台账"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    eval_id: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, comment="评估集题号,如 A43;一题一行")
    bucket: Mapped[str] = mapped_column(VARCHAR(24), nullable=False, comment="题目所属桶:A_policy / B_model / C_colloquial / E_multi")
    query: Mapped[str] = mapped_column(VARCHAR(512), nullable=False, comment="用户问题原文")
    strategy: Mapped[str] = mapped_column(VARCHAR(24), nullable=False, server_default=text("'hybrid_rerank'"), comment="产出这条答案的检索策略")
    answer: Mapped[str] = mapped_column(TEXT, nullable=False, comment="被判编造的那版生成答案原文")
    reason: Mapped[str] = mapped_column(TEXT, nullable=False, comment="裁判给的理由:编在哪一句")
    citations: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON(none_as_null=True), nullable=True, comment="这一轮喂给模型的 Top-K 证据全集快照:[{n,chunk_id,section_path,question,answer}];答案里的角标 [n] 就是这份列表的序号,答案通常只引用其中两三条;老数据没记为 NULL")
    judge_model: Mapped[str | None] = mapped_column(VARCHAR(64), nullable=True, comment="判这条的裁判模型")
    status: Mapped[str] = mapped_column(ENUM("未解决", "已解决", "无需解决"), nullable=False, server_default=text("'未解决'"), comment="处置状态,人工点按钮改")
    seen_count: Mapped[int] = mapped_column(INTEGER(unsigned=True), nullable=False, server_default=text("1"), comment="被判编造的累计次数(跨轮)")
    first_seen_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="第一次被判编造的时间")
    last_seen_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="最近一次被判编造的时间")
    resolution: Mapped[str | None] = mapped_column(VARCHAR(300), nullable=True, comment="处置说明:标已解决要写清怎么解决的,标无需解决要写清为什么不用改;退回未解决时清空。空着的处置在台账上等于没有交代")
    resolved_at: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True, comment="最近一次被标为已解决/无需解决的时间;复发后仍保留,用来标「复发」")
