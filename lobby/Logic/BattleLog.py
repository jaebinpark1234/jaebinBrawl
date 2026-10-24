"""
BattleLog — 전투 기록 저장/조회.

배틀이 끝나면(14110 AskForBattleEndMessage) Database/BattleLog/<low_id>.json 에
기록을 쌓고, 프로필 조회(14113 AskProfileMessage) 시 BattleLogMessage(23458)로
돌려준다.
"""

import json
import os
import time

LOG_DIR = 'Database/BattleLog'
MAX_ENTRIES = 50


def _path(low_id):
    os.makedirs(LOG_DIR, exist_ok=True)
    return os.path.join(LOG_DIR, f'{low_id}.json')


def save_battle_log(player, battle_end_message):
    """배틀 종료 패킷(AskForBattleEndMessage)에서 기록 한 건을 저장한다."""
    entry = {
        'time': int(time.time()),
        'battleType': 1,                                   # 1 = Normal, 2 = Crash, 3 = Survived
        'map': getattr(battle_end_message, 'map', 0),
        'result': getattr(player, 'battle_result', 0),     # 클라이언트가 보고한 결과
        'rank': getattr(battle_end_message, 'rank', 0),
        'players': getattr(battle_end_message, 'players', 0),
        'team': getattr(player, 'team', 0),
        'brawler': getattr(player, 'brawler_id', 0),
        'trophiesResult': 8 if getattr(player, 'battle_result', 0) == 0 else 0,  # 승리 가정: 8 / 기타 0
        'battleTime': 120,
    }
    entries = load_battle_log(player, limit=None)
    entries.append(entry)
    entries = entries[-MAX_ENTRIES:]
    with open(_path(player.low_id), 'w') as log_file:
        json.dump(entries, log_file)
    print(f'[INFO] Battle log saved for player {player.low_id} (total {len(entries)})')
    return entry


def load_battle_log(player, limit=MAX_ENTRIES):
    """저장된 전투 기록을 최신순으로 돌려준다."""
    try:
        with open(_path(player.low_id)) as log_file:
            entries = json.load(log_file)
    except (OSError, ValueError):
        return []
    entries.sort(key=lambda e: e.get('time', 0), reverse=True)
    if limit is not None:
        entries = entries[:limit]
    return entries