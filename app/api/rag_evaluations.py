"""本机评估工作台：固定请求边界、只读快照和已提交公开报告下载。"""

import copy
from datetime import datetime
import json
from pathlib import Path as FilePath
from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field

from app.config import Settings
from app.rag_evaluation.dataset import DATASET_ID, DatasetError, load_dataset
from app.rag_evaluation.export import MAX_EXPORT_BYTES, render_markdown, report_envelope
from app.rag_evaluation.locking import RunBusy
from app.rag_evaluation.manager import DATASET_ROOT, PROJECT_ROOT, PilotRequired, RunManager
from app.rag_evaluation.report import public_report
from app.rag_evaluation.store import OUTCOMES, RunStore, StoreError, guarded_path, public_run_metadata

PREFIX = '/api/rag-evaluations'
LEGACY_ID = 'legacy-30-v1'
LEGACY_FILE = PROJECT_ROOT / 'app/static/rag-evaluation-history.json'
Strategy = Literal['dense', 'bm25', 'hybrid', 'hybrid_rerank']
RunId = Annotated[str, Path(pattern=r'^(?:[0-9a-f]{32}|legacy-30-v1)$')]
EvalId = Annotated[str, Path(pattern=r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')]
ERRORS = {
    'evaluation_disabled': (403, '评估运行功能未启用。'),
    'origin_forbidden': (403, '请求来源不在本机工作台白名单。'),
    'json_required': (415, '写请求必须使用 application/json。'),
    'invalid_request': (422, '请求参数不合法。'),
    'run_busy': (409, '已有评估运行或清理尚未结束。'),
    'pilot_required': (409, '需要先完成同配置的合法试运行。'),
    'legacy_readonly': (409, '历史报告为只读记录。'),
    'not_found': (404, '运行或逐题记录不存在。'),
    'export_unavailable': (409, '最终报告尚未完成一致发布。'),
    'dataset_invalid': (422, '冻结数据集校验失败。'),
    'storage_unavailable': (503, '评估记录暂时不可用。'),
    'evaluation_error': (500, '评估请求处理失败。'),
}


class PublicError(Exception):
    """仅允许固定错误码跨越 HTTP 边界，不携带输入或异常正文。"""

    def __init__(self, code: str):
        """记录登记错误码，状态与消息统一由白名单决定。"""
        self.code = code


def _error(code: str) -> JSONResponse:
    """公开错误始终只有 code/message，不回显 Pydantic input 或 SDK 异常。"""
    status, message = ERRORS[code]
    return JSONResponse(status_code=status, content={'code': code, 'message': message})


class SafeRoute(APIRoute):
    """只在工作台范围清洗异常，保持既有聊天与 SSE 错误契约。"""

    def get_route_handler(self):
        """在参数解析前验证写请求，在响应前统一处理安全错误。"""
        original = super().get_route_handler()

        async def handle(request: Request):
            """任何非法写请求在管理器之前停止，未知异常也不返回原文。"""
            try:
                if request.method == 'POST':
                    _guard_write(request, self.evaluation_settings)
                if len(request.query_params.multi_items()) != len(set(request.query_params.keys())):
                    raise PublicError('invalid_request')
                return await original(request)
            except PublicError as exc:
                return _error(exc.code)
            except RequestValidationError:
                return _error('invalid_request')
            except RunBusy:
                return _error('run_busy')
            except PilotRequired:
                return _error('pilot_required')
            except DatasetError:
                return _error('dataset_invalid')
            except (StoreError, OSError):
                return _error('storage_unavailable')
            except Exception:
                return _error('evaluation_error')

        return handle


def _guard_write(request: Request, settings: Settings) -> None:
    """Host 与可选 Origin 都须指向同一个显式本机来源，忽略代理头。"""
    if not settings.rag_evaluation_enabled:
        raise PublicError('evaluation_disabled')
    if request.headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'application/json':
        raise PublicError('json_required')
    hosts, origins = request.headers.getlist('host'), request.headers.getlist('origin')
    if len(hosts) != 1 or len(origins) > 1:
        raise PublicError('origin_forbidden')
    local_origin = f'{request.url.scheme}://{hosts[0]}'
    if (local_origin not in settings.rag_evaluation_allowed_origins
            or (origins and origins[0] != local_origin)):
        raise PublicError('origin_forbidden')
    if request.query_params:
        raise PublicError('invalid_request')


class EmptyParams(BaseModel):
    """没有参数的接口也拒绝额外键，避免隐藏输出路径或运行配置入口。"""
    model_config = ConfigDict(extra='forbid')


class StartRequest(EmptyParams):
    """启动只接受冻结版本与范围，禁止调用方指定模型、阈值或落点。"""
    model_config = ConfigDict(extra='forbid', strict=True)
    dataset_id: Literal['merchant-rag-300-v1']
    scope: Literal['pilot', 'full']


class PageParams(EmptyParams):
    """URL 整数字符串按 HTTP 规则解析，分页限制用于历史与逐题列表。"""
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class CaseParams(PageParams):
    """过滤只允许登记枚举，关键词最多 512 字符且不执行正则或 SQL。"""
    bucket: Literal['A_policy', 'B_model', 'C_colloquial', 'E_multi', 'D_absent', 'D_unanswerable'] | None = None
    strategy: Strategy | None = None
    status: Literal['running', 'completed', 'rewrite_error', 'retrieval_error', 'self_check_error',
        'answer_error', 'judge_error', 'cancelled', 'not_attempted', 'ok', 'error'] | None = None
    query: str | None = Field(default=None, max_length=512)


class ExportParams(EmptyParams):
    """下载仅开放两种公开格式，参数不能映射任意服务器路径。"""
    format: Literal['json', 'markdown'] = 'json'


def _legacy() -> dict:
    """历史字节保持不变，通过既有 v1 适配器去掉请求正文与私密裁判。"""
    result = public_report(json.loads(LEGACY_FILE.read_text(encoding='utf-8')))
    result['run'] = {'run_id': LEGACY_ID, 'dataset_id': LEGACY_ID, 'schema_version': 1,
        'mode': 'legacy', 'state': 'completed', 'read_only': True, 'counts': result['counts']}
    result.update(run_id=LEGACY_ID, dataset_id=LEGACY_ID)
    return result


def _page(items: list[dict], params: PageParams) -> dict:
    """总数为过滤后实际记录数，缺席计划由运行计数单独表示。"""
    return {'items': items[params.offset:params.offset + params.limit], 'total': len(items),
        'offset': params.offset, 'limit': params.limit}


async def _manifest(store: RunStore, run_id: str) -> dict:
    """只访问严格 UUID 固定 manifest，不存在与损坏文件分别给出安全错误。"""
    if not guarded_path(store.root, run_id, 'manifest.json').is_file():
        raise PublicError('not_found')
    return await store.get(run_id, persist_repair=False)


async def _snapshot(store: RunStore, run_id: str) -> dict:
    """读取同一循环内实际检查点及当前 manifest，无 await 间隙造成虚假进度。"""
    if run_id == LEGACY_ID:
        return _legacy()
    manifest = await _manifest(store, run_id)
    records = await store.records(run_id, persist_repair=False)
    # 两个 store 方法内部有同步临界区；重复读使跨进程检查点变更体现在计数中。
    manifest = await store.get(run_id, persist_repair=False)
    return report_envelope(manifest, records)


def _export_paths(store: RunStore, run_id: str, current: dict) -> dict[str, FilePath]:
    """终态为提交标记；两份导出须同当前公开封套一致才允许下载。"""
    if current['run']['state'] not in OUTCOMES:
        raise PublicError('export_unavailable')
    paths = {name: guarded_path(store.root, run_id, name) for name in ('report.json', 'report.md')}
    if any(not path.is_file() or path.stat().st_size > MAX_EXPORT_BYTES for path in paths.values()):
        raise PublicError('export_unavailable')
    try:
        raw = paths['report.json'].read_bytes()
        saved = json.loads(raw)
        if (not isinstance(saved, dict) or not isinstance(saved.get('run'), dict)
                or set(saved['run']) != set(current['run'])
                or raw != json.dumps(saved, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')):
            raise PublicError('export_unavailable')
        clock = saved['run']['updated_at']
        if not isinstance(clock, str) or len(clock) > 40:
            raise PublicError('export_unavailable')
        published = datetime.fromisoformat(clock)
        if (published.utcoffset() is None or published.isoformat() != clock
                or not datetime.fromisoformat(current['run']['created_at']) <= published
                    <= datetime.fromisoformat(current['run']['updated_at'])):
            raise PublicError('export_unavailable')
        comparison = copy.deepcopy(saved)
        expected = copy.deepcopy(current)
        # manager 完整报告先发布，随后 manifest 更新最后的发布时钟。
        comparison['run'].pop('updated_at', None)
        expected['run'].pop('updated_at', None)
        # JSON 比较保留 bool/int/float 类型，避免 Python 的 True == 1 放过非法 DTO。
        if (json.dumps(comparison, ensure_ascii=False, sort_keys=True, allow_nan=False)
                != json.dumps(expected, ensure_ascii=False, sort_keys=True, allow_nan=False)
                or paths['report.md'].read_bytes() != render_markdown(saved).encode('utf-8')):
            raise PublicError('export_unavailable')
    except (ValueError, KeyError, TypeError):
        raise PublicError('export_unavailable') from None
    return paths


def create_router(manager: RunManager, store: RunStore, settings: Settings) -> APIRouter:
    """组装九类接口；GET 只使用离线资料、存储和公开投影，无模型入口。"""
    settings = settings.model_copy(deep=True)
    class BoundRoute(SafeRoute):
        """每个工厂实例保留独立启动配置，挂载不依赖宿主应用 state。"""
        evaluation_settings = settings
    router = APIRouter(route_class=BoundRoute)

    @router.get('/rag-eval', include_in_schema=False)
    async def page(params: Annotated[EmptyParams, Query()]):
        """直接返回既有静态预览，前端接入由后续任务负责。"""
        return FileResponse(PROJECT_ROOT / 'app/static/rag-evaluation.html')

    @router.get(PREFIX + '/datasets')
    async def datasets(params: Annotated[EmptyParams, Query()]):
        """只读核验真实冻结资料和管理器匹配门槛，默认禁用时仍展示版本。"""
        dataset = load_dataset(DATASET_ID, root=DATASET_ROOT)
        ready = await manager.pilot_ready(DATASET_ID)
        scopes = ['pilot', 'full'] if ready else ['pilot']
        return {'enabled': settings.rag_evaluation_enabled, 'items': [{
            'dataset_id': dataset.dataset_id, 'fingerprint': dataset.fingerprint,
            'corpus_hash': dataset.corpus_hash, 'cases_hash': dataset.cases_hash,
            'annotation_hash': dataset.annotation_hash, 'case_count': len(dataset.cases),
            'chunk_count': len(dataset.chunks), 'pilot_case_count': len(dataset.pilot_ids),
            'strategies': ['dense', 'bm25', 'hybrid', 'hybrid_rerank'], 'mode': 'content_ablation',
            'matching_pilot': ready, 'available_scopes': scopes if settings.rag_evaluation_enabled else []}]}

    @router.post(PREFIX + '/runs', status_code=202)
    async def start(body: StartRequest):
        """验证后交给 lifespan 管理器创建单个运行，不使用请求 BackgroundTasks。"""
        return {'run_id': await manager.start(body.dataset_id, body.scope)}

    @router.get(PREFIX + '/runs')
    async def history(params: Annotated[PageParams, Query()]):
        """运行历史包含固定只读旧报告，分页不会触发模型或启动恢复。"""
        values, offset = [], 0
        while True:
            rows = await store.list_runs(offset, 100, persist_repair=False)
            values.extend(dict(public_run_metadata(row), read_only=False) for row in rows)
            if len(rows) < 100:
                break
            offset += len(rows)
        values.append(_legacy()['run'])
        return _page(values, params)

    @router.get(PREFIX + '/runs/{run_id}')
    async def run(run_id: RunId, params: Annotated[EmptyParams, Query()]):
        """返回当前状态、冻结配置和实际记录汇总，私有归属永不公开。"""
        result = await _snapshot(store, run_id)
        result.pop('records', None)
        result['run']['read_only'] = run_id == LEGACY_ID
        return result

    @router.get(PREFIX + '/runs/{run_id}/cases')
    async def cases(run_id: RunId, params: Annotated[CaseParams, Query()]):
        """按公开记录的登记字段过滤并分页，D_absent 兼容内部旧桶名。"""
        rows = (await _snapshot(store, run_id))['records']
        normalize = {'D_unanswerable': 'D_absent'}
        selected = [row for row in rows if
            (params.bucket is None or normalize.get(row.get('bucket'), row.get('bucket')) == normalize.get(params.bucket, params.bucket))
            and (params.strategy is None or row['strategy'] == params.strategy)
            and (params.status is None or row['status'] == params.status)
            and (params.query is None or params.query.casefold() in (row['eval_id'] + ' ' + row.get('query', '')).casefold())]
        return _page(selected, params)

    @router.get(PREFIX + '/runs/{run_id}/cases/{eval_id}/{strategy}')
    async def case(run_id: RunId, eval_id: EvalId, strategy: Strategy, params: Annotated[EmptyParams, Query()]):
        """单条严格公开记录包含实际证据与判定，缺席计划详情返回404。"""
        if '--' in eval_id:
            raise PublicError('invalid_request')
        for row in (await _snapshot(store, run_id))['records']:
            if row['eval_id'] == eval_id and row['strategy'] == strategy:
                return row
        raise PublicError('not_found')

    @router.post(PREFIX + '/runs/{run_id}/cancel')
    async def cancel(run_id: RunId, body: EmptyParams):
        """空 JSON 取消，旧报告拒绝而终态返回现有状态，不删除或重跑。"""
        if run_id == LEGACY_ID:
            raise PublicError('legacy_readonly')
        await _manifest(store, run_id)
        await manager.cancel(run_id)
        return public_run_metadata(await store.get(run_id, persist_repair=False))

    @router.get(PREFIX + '/runs/{run_id}/export')
    async def export(run_id: RunId, params: Annotated[ExportParams, Query()]):
        """新报告只读下载已提交固定文件；旧版只导出白名单适配后的内容。"""
        if run_id == LEGACY_ID:
            value = _legacy()
            text = json.dumps(value, ensure_ascii=False, indent=2)
            content = text if params.format == 'json' else '# 旧版只读 RAG 报告\n\n```json\n' + text + '\n```\n'
            return Response(content, media_type='application/json' if params.format == 'json' else 'text/markdown',
                headers={'Content-Disposition': f'attachment; filename="{LEGACY_ID}.{"json" if params.format == "json" else "md"}"'})
        snapshot = await _snapshot(store, run_id)
        paths = _export_paths(store, run_id, snapshot)
        name = 'report.json' if params.format == 'json' else 'report.md'
        return FileResponse(paths[name], filename=f'{run_id}.{"json" if params.format == "json" else "md"}',
            media_type='application/json' if params.format == 'json' else 'text/markdown')

    return router
