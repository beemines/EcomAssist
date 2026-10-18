from app.tools.catalog_types import fingerprint
from app.tools.types import ToolOutcome


def denied(message='该工具调用尚未获得用户确认或本地权限。'):
    return ToolOutcome({'error': {'code': 'permission_denied', 'message': message}}, 'error', 0)


def authorize_call(definition, call, context):
    if context.policy is not None:
        policy = context.policy.load() if hasattr(context.policy, 'load') else context.policy
        rule = policy.rule(definition.source, definition.name)
        if rule is None or rule['operation'] != definition.operation:
            return denied('该工具权限已撤销。')
        if rule.get('allowed_intents') and context.intent not in rule['allowed_intents']:
            return denied('当前场景不允许该工具。')
    if definition.allowed_intents and context.intent not in definition.allowed_intents:
        return denied('当前场景不允许该工具。')
    if definition.operation == 'write':
        grant = context.grant
        if (definition.source != 'builtin' or definition.name != 'create_ticket'
                or grant is None or grant.source not in ('chat_preview', 'legacy_form')
                or grant.conversation_id != context.conversation_id
                or grant.user_message_id != context.user_message_id
                or grant.tool_call_id != call.id
                or grant.arguments_fingerprint != fingerprint(call.args)
                or grant.source == 'chat_preview' and not context.ticket_requested):
            return denied()
    return None
