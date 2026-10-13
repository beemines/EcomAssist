"""Workflow 生命周期日志只记录身份和阶段，不记录用户正文。"""
import logging

logger = logging.getLogger(__name__)


def log_lifecycle(prepared, phase, **metadata):
    """记录可关联 SQL 和检查点的运行边界，避免泄漏内部控制内容。"""
    logger.info('workflow_lifecycle', extra={'workflow': {
        'conversation_id': prepared.conversation_id,
        'user_message_id': str(prepared.user_message_id), 'phase': phase, **metadata}})
