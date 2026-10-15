"""本机确认动作边界：严格同源 JSON 和固定安全错误。"""
from urllib.parse import urlsplit

from fastapi import APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.errors import ServiceError
from app.schemas.chat_actions import TicketActionRequest


ERRORS = {
    'selection_conflict': (409, '选单已经失效或与本轮不匹配，请重新发起。'),
    'service_unavailable': (503, '服务暂时不可用，请稍后重试。'),
    'upstream_timeout': (504, '本轮处理超时，请重新发起。'),
    'origin_forbidden': (403, '请求来源不在本机白名单。'),
    'json_required': (415, '写请求必须使用 application/json。'),
    'invalid_request': (422, '请求参数不合法。'),
    'invalid_conversation_id': (422, '会话身份无效。'),
    'action_not_found': (404, '完成快照不存在。'),
    'invalid_action': (422, '该回复不允许创建工单。'),
    'conversation_not_found': (404, '会话不存在。'),
    'conversation_ended': (409, '会话已经结束。'),
    'invalid_user_message': (422, '用户消息不属于当前会话。'),
    'session_busy': (409, '会话正在处理其他请求。'),
    'ticket_conflict': (409, '工单身份与已有业务内容冲突。'),
    'tool_timeout': (503, '工单执行超时，请稍后重试。'),
    'tool_connection_error': (503, '工单连接暂时不可用，请稍后重试。'),
    'tool_execution_error': (503, '工单暂时无法创建，请稍后重试。'),
}


def _guard_write(request: Request):
    """独立验证本机 Host 与同源 Origin，不信任任意 Host 或代理头。"""
    if request.headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'application/json':
        raise ServiceError('json_required', '', 415)
    hosts, origins = request.headers.getlist('host'), request.headers.getlist('origin')
    if len(hosts) != 1 or len(origins) > 1:
        raise ServiceError('origin_forbidden', '', 403)
    local_origin = f'{request.url.scheme}://{hosts[0]}'
    try:
        parsed = urlsplit(local_origin)
        port = parsed.port
        loopback = parsed.hostname in ('127.0.0.1', 'localhost', '::1')
        canonical = (parsed.scheme in ('http', 'https') and parsed.netloc == hosts[0]
            and parsed.username is None and parsed.password is None
            and not parsed.path and not parsed.query and not parsed.fragment
            and (port is None or 1 <= port <= 65535))
    except ValueError:
        canonical = loopback = False
    whitelist = request.app.state.chat_action_allowed_origins
    if (not canonical or not (loopback or local_origin in whitelist)
            or (origins and origins[0] != local_origin) or (not origins and not loopback)):
        raise ServiceError('origin_forbidden', '', 403)
    if request.query_params:
        raise ServiceError('invalid_request', '', 422)


class ActionRoute(APIRoute):
    """只清洗本确认接口的错误，不改变聊天 SSE 的现有契约。"""
    def get_route_handler(self):
        """在请求解析前拦截非法来源，统一屏蔽输入和内部异常正文。"""
        original = super().get_route_handler()

        async def handle(request: Request):
            """只返回白名单错误码及安全消息，取消异常继续传播。"""
            try:
                if request.method != 'GET':
                    _guard_write(request)
                return await original(request)
            except RequestValidationError:
                code = 'invalid_request'
            except ServiceError as exc:
                code = exc.code if exc.code in ERRORS else 'tool_execution_error'
            except Exception:
                code = 'tool_execution_error'
            status, message = ERRORS[code]
            return JSONResponse(status_code=status, content={'code': code, 'message': message})

        return handle


router = APIRouter(route_class=ActionRoute)


@router.post('/api/conversations/{conversation_id}/actions/ticket')
async def create_ticket(conversation_id: str, payload: TicketActionRequest, request: Request) -> dict:
    """明确提交入口传递已校验表单，动作服务另外核对原回复与会话归属。"""
    service = request.app.state.ticket_action_service
    if service is None:
        raise ServiceError('tool_execution_error', '', 503)
    return await service.create_ticket(conversation_id, payload)
