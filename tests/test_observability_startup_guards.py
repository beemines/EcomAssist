import json
from pathlib import Path
from tests.test_tool_system_demo_ownership import powershell


def test_pid_reuse_command_path_and_ancestry_are_required(tmp_path):
    helper=Path('scripts/observability-process-ownership.ps1').resolve().as_posix()
    result=powershell(tmp_path,r'''
$ErrorActionPreference='Stop'
. 'HELPER'
$root='D:\project'; $exe='C:\Python\python.exe'; $command=Get-ObservabilityCommand $root
$launch=[pscustomobject]@{ProcessId=20;ParentProcessId=1;CreationDate=[datetime]'2026-10-20T01:00:00Z';ExecutablePath=(Join-Path $root '.venv\Scripts\python.exe');CommandLine=$command}
$child=[pscustomobject]@{ProcessId=21;ParentProcessId=20;CreationDate=[datetime]'2026-10-20T01:00:01Z';ExecutablePath=$exe;CommandLine=('"'+$exe+'"  '+$command.Substring($command.IndexOf('" ')+2))}
$owner=[pscustomobject]@{root=$root;interpreter=$exe;command=$command;launch=(New-ContextProcessIdentity $launch);listener=(New-ContextProcessIdentity $child)}
$valid=Test-ObservabilityOwner $child $owner $root $exe @($launch,$child)
$child.CreationDate=$child.CreationDate.AddSeconds(1)
$reuse=Test-ObservabilityOwner $child $owner $root $exe @($launch,$child)
$child.CreationDate=$child.CreationDate.AddSeconds(-1)
$path=Test-ObservabilityOwner $child $owner 'D:\other' $exe @($launch,$child)
$child.CommandLine+=' --reload'
$commandBad=Test-ObservabilityOwner $child $owner $root $exe @($launch,$child)
@($valid,$reuse,$path,$commandBad)|ConvertTo-Json -Compress
'''.replace('HELPER',helper))
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)==[True,False,False,False]


def test_unknown_listener_is_never_started_or_stopped(tmp_path):
    # A launcher test owns its script root and journal; never consume the live
    # checkout's owner file or an in-progress browser acceptance journal.
    scripts=tmp_path/'scripts';scripts.mkdir()
    for name in ('start-observability-demo.ps1','observability-process-ownership.ps1',
                 'tool-system-process-ownership.ps1','context-process-ownership.ps1'):
        (scripts/name).write_bytes((Path('scripts')/name).read_bytes())
    journal=tmp_path/'runtime/ch09-evidence/acceptance-owned-jobs.json'
    journal.parent.mkdir(parents=True);journal.write_text('{"closed":false}',encoding='utf-8')
    launcher=(scripts/'start-observability-demo.ps1').as_posix()
    result=powershell(tmp_path,'''
$ErrorActionPreference='Stop'
function Get-NetTCPConnection { [pscustomobject]@{OwningProcess=987654} }
function Stop-Process { throw 'UNSAFE_STOP' }
function Start-Process { throw 'UNSAFE_START' }
try { & 'LAUNCHER'; throw 'Unexpected success' }
catch { if($_.Exception.Message -match 'unowned|ownership mismatch') { 'REFUSED';exit 0 };throw }
'''.replace('LAUNCHER',launcher))
    assert result.returncode==0 and 'REFUSED' in result.stdout,result.stderr


async def test_new_demo_does_not_summarize_old_backlog():
    from app.context.manager import SummaryManager
    class Repo:
        async def list_downgraded(self,**kwargs): raise AssertionError('old conversations read')
    manager=SummaryManager(Repo(),None,budget_provider=lambda:None)
    await manager.startup(recover_existing=False)
    await manager.aclose()


async def test_intent_statistics_read_rejects_nonlocal_host():
    import httpx
    from fastapi import FastAPI
    from app.api.observability import router
    app=FastAPI();app.state.chat_action_allowed_origins=[];app.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://127.0.0.1:8006') as client:
        assert (await client.get('/api/observability/intent-usage')).status_code==200
        assert (await client.get('/api/observability/intent-usage',headers={'host':'evil.invalid'})).status_code==403


def test_demo_prefers_available_reference_rule_without_overwriting_original(tmp_path,monkeypatch):
    from app.observability.demo import load_ch09_settings
    monkeypatch.delenv('CH09_SETTINGS_FILE',raising=False)
    sdk=tmp_path/'runtime/langfuse';sdk.mkdir(parents=True)
    sdk.joinpath('sdk.env').write_text('LANGFUSE_ENABLED=true\nLANGFUSE_BASE_URL=http://127.0.0.1:3000\n'
        'LANGFUSE_PUBLIC_KEY=pk-offline\nLANGFUSE_SECRET_KEY=sk-offline\n',encoding='utf-8')
    tmp_path.joinpath('.env').write_text('LLM_MODEL=fake-chat\nLLM_API_KEY=offline\nLLM_BASE_URL=https://upstream.invalid/v1\n',encoding='utf-8')
    original=tmp_path/'runtime/ch09-evidence/calibration/rule.json'
    original.parent.mkdir(parents=True);original.write_text('original',encoding='utf-8')
    assert load_ch09_settings(tmp_path).evidence_confidence_rule_path==original
    newer=tmp_path/'runtime/ch09-evidence/reference-calibration/rule.json'
    newer.parent.mkdir(parents=True);newer.write_text('reference',encoding='utf-8')
    assert load_ch09_settings(tmp_path).evidence_confidence_rule_path==newer
    assert original.read_text(encoding='utf-8')=='original'
