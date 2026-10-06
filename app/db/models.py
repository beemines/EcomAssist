from datetime import datetime
from typing import Any

from sqlalchemy import FetchedValue, ForeignKey, Index, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, ENUM, JSON, TEXT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """只映射已有表；建表始终由用户提供的 sql/schema.sql 执行。"""


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("idx_user_id", "user_id"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "客服会话"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="会话主键")
    user_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment="用户标识")
    status: Mapped[str] = mapped_column(ENUM("进行中", "已转人工", "已结束"), nullable=False, server_default=text("'进行中'"), comment="处理状态")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="开启时间")
    updated_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), server_onupdate=FetchedValue(), comment="更新时间")


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


class FAQ(Base):
    __tablename__ = "faq"
    __table_args__ = (Index("idx_category", "category"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "常见问答"})

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="FAQ 主键")
    question: Mapped[str] = mapped_column(VARCHAR(512), nullable=False, comment="问题")
    answer: Mapped[str] = mapped_column(TEXT, nullable=False, comment="答案")
    category: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment="分类")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), server_onupdate=FetchedValue(), comment="更新时间")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (Index("idx_conversation_id", "conversation_id"), {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "人工工单"})

    ticket_no: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True, comment="工单号,如 T20260701008")
    conversation_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey("conversations.id", name="fk_tickets_conversation"), nullable=False, comment="关联会话,可倒查当时聊了什么")
    description: Mapped[str] = mapped_column(TEXT, nullable=False, comment="问题描述")
    ticket_type: Mapped[str] = mapped_column(ENUM("售后", "投诉", "咨询"), nullable=False, comment="工单类型")
    status: Mapped[str] = mapped_column(ENUM("待处理", "已处理"), nullable=False, server_default=text("'待处理'"), comment="处理状态")
    created_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
