"""
BattleLog — 전투 기록 저장/조회.
Database/BattleLog/<id>.json 에 전적을 쌓고 BattleLogMessage(23458)로 전송.
"""

import json
import os
import time

LOG_DIR = 'Database/BattleLog'
MAX_ENTRIES = 50


def _path(player_id):
    os.makedirs(LOG_DIR, exist_ok=True)
    return os.path.join(LOG_DIR, f'{player_id}.json')


def save_battle_log(player, map_id=7, result=0, trophies_result=8):
    entry = {
        'time': int(time.time()),
        'battleType': 1,
        'map': map_id,
        'result': result,
        'trophiesResult': trophies_result,
        'battleTime': 120,
        'players': 6,
        'team': 0,
        'brawler': getattr(player, 'home_brawler', 0),
    }
    entries = load_battle_log(player, limit=None)
    entries.append(entry)
    entries = entries[-MAX_ENTRIES:]
    try:
        with open(_path(player.ID), 'w') as f:
            json.dump(entries, f)
    except Exception as e:
        print(f"[WARN] Failed to save battle log: {e}")
    return entry


def load_battle_log(player, limit=MAX_ENTRIES):
    try:
        with open(_path(player.ID), 'r') as f:
            entries = json.load(f)
    except Exception:
        return []
    entries.sort(key=lambda e: e.get('time', 0), reverse=True)
    if limit is not None:
        entries = entries[:limit]
    return entries
