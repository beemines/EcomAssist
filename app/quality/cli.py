# 质量管理命令提供原样迁移、台账查看与人工处置，失败只打印异常类型。
import argparse
import asyncio
import json
import sys

from app.config import load_settings
from app.db.session import Database
from app.quality.migration import migrate_quality
from app.quality.repository import QualityRepository
from app.quality.types import CASE_STATUSES, require_text, resolution_value


class QualityParser(argparse.ArgumentParser):
    # 参数解析后检查处置说明，使非法输入在创建数据库连接之前失败。
    def parse_args(self, args=None, namespace=None):
        result = super().parse_args(args, namespace)
        if result.command == "resolve":
            try:
                require_text("eval_id", result.eval_id, 16)
                resolution_value(result.status, result.resolution)
            except ValueError:
                self.error("处置题号必须有效；已解决/无需解决须提供非空且不超过 300 字的说明")
        return result


# 定义迁移、按状态列出个案和按题号处置的命令参数。
def parser() -> argparse.ArgumentParser:
    result = QualityParser(description="质量问题池与忠实度台账管理")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate", help="执行或核验用户原始质量 DDL")
    cases = commands.add_parser("cases", help="列出忠实度个案")
    cases.add_argument("--status", choices=CASE_STATUSES)
    resolve = commands.add_parser("resolve", help="处置指定评估题号")
    resolve.add_argument("--eval-id", required=True)
    resolve.add_argument("--status", choices=CASE_STATUSES, required=True)
    resolve.add_argument("--resolution")
    return result


# 创建数据库依赖并执行命令，任何路径退出时都释放连接池。
async def run(args: argparse.Namespace) -> None:
    database = Database(load_settings().database_url)
    try:
        repository = QualityRepository(database)
        if args.command == "migrate":
            await migrate_quality(database)
            print("Quality schema ready")
        elif args.command == "cases":
            print(json.dumps(await repository.list_cases(args.status), ensure_ascii=False, default=str))
        elif args.command == "resolve":
            await repository.resolve_case(args.eval_id, args.status, args.resolution)
            print("Case updated")
    finally:
        await database.dispose()


# 运行异步命令并映射退出码，配置和驱动异常不得泄露凭据或内部文本。
def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        asyncio.run(run(args))
    except Exception as exc:
        print(f"Quality job failed ({type(exc).__name__}); check configuration and input", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
