from datetime import datetime, timezone
import random


def order_key(order_id: str) -> str:
    if not isinstance(order_id, str) or not order_id.strip() or len(order_id) > 64:
        raise ValueError('请提供有效订单号。')
    return order_id


def logistics(order_id: str, *, rng=random) -> dict:
    return {'order_id': order_key(order_id), 'mock': True, 'source': 'mcp:logistics',
        'status': rng.choice(['已揽收', '运输中', '派送中', '已签收']),
        'tracking_no': 'MOCK' + str(rng.randint(10000000, 99999999)),
        'events': [{'location': rng.choice(['成都分拨中心', '上海转运中心', '北京配送站']),
                    'description': '模拟物流轨迹更新', 'time': datetime.now(timezone.utc).isoformat()}]}


def warranty(order_id: str, *, rng=random) -> dict:
    return {'order_id': order_key(order_id), 'mock': True, 'source': 'mcp:aftersales',
        'warranty_status': rng.choice(['在保', '已过保']), 'warranty_months': 12,
        'note': '随机演示在保数据，不作为实际售后承诺。'}


def return_progress(order_id: str, *, rng=random) -> dict:
    return {'order_id': order_key(order_id), 'mock': True, 'source': 'mcp:aftersales',
        'return_status': rng.choice(['待寄回', '仓库验收中', '审核中', '已完成']),
        'note': '随机模拟退货进度，不表示已执行真实退款。'}
