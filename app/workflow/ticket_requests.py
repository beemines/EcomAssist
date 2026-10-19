"""Traceable user request evidence, independent of model-generated descriptions."""
import re
from app.workflow.intent import has_explicit_ticket_request


def ticket_request_for_turn(identifier, question, previous, *, previous_verified=False):
    if has_explicit_ticket_request(question):
        return {'origin_user_message_id': str(identifier), 'request_text': question,
                'source_message_ids': [str(identifier)], 'source_texts': [question]}
    if (not previous_verified or previous.get('intent') != '工单'
            or previous.get('reply_mode') != 'clarification'
            or not previous.get('ticket_request')
            or re.search(r'(?:不要|不用|不想|别|取消).*(?:工单|建单)|(?:只|改|先).*(?:物流|订单|退货|退款|转人工)', question)):
        return None
    request = previous['ticket_request']
    return {**request, 'source_message_ids': [*request['source_message_ids'], str(identifier)],
            'source_texts': [*request['source_texts'], question]}


def description_sources(request):
    """Non-request user text in this verified scope; adequacy still belongs to the Agent."""
    if not request:
        return ()
    issues = []
    for source in request.get('source_texts', []):
        issue = re.sub(r'(?:请(?:您|你)?|麻烦(?:您|你)?)?(?:帮我|给我|帮忙|我要|我想)?(?:创建|提交|建|开)[个一张份]*(?:售后|投诉|咨询)?工单(?:吧|吗)?', '', source)
        issue = re.sub(r'^[，。！？!?,;；：:\s]+', '', issue)
        if re.search(r'\w', issue):
            issues.append(issue)
    return tuple(issues)


def grounded_description(description, request):
    if not isinstance(description, str) or not re.search(r'\w', description):
        return False
    return any(description in issue for issue in description_sources(request))
