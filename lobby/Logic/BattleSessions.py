"""
BattleSessions — 로비 ↔ C# 배틀 서버(UDP 1337) 핸드셰이크 연동부.

역할:
  1. 배틀 시작 시 배틀 ID(battle_id)를 배정하고,
     세션 ID(sid = battle_id * 100 + 슬롯)를 생성한다.
  2. C# 배틀 서버(Atrasis.Laser.Battle, UDP 1337)로 UDP 등록 패킷을 먼저 보내
     세션의 게임 모드/소속 배틀을 미리 알려준다 (마커 0xFFFF).
  3. 클라이언트에게 TeamGameStartingDataMessage(24109)로 접속 정보
     (배틀 서버 IP / UDP 포트 1337, sid)를 전송하여 배틀 세션으로 진입시킨다.
"""

import os
import random
import socket
import struct
import json

# ── C# BattleModeRegistry.cs 상수 ──────────────────────────────────────────
MODE_GEMGRAB = 0
MODE_SHOWDOWN = 2        # 솔로 10인 / 듀오 5팀 10인
MODE_HEIST = 3
MODE_BOUNTY = 4
MODE_BRAWLBALL = 5       # C# 배틀 서버 기본 구현 모드
MODE_ROBORUMBLE = 6
MODE_BOSSFIGHT = 7
MODE_BIGGAME = 8
MODE_LONESTAR = 11
MODE_TAKEDOWN = 12
MODE_PRESENTPLUNDER = 13

REGISTRATION_MARKER = -1  # 0xFFFF (short)

MAP_INDEX_TO_MODE = {
    1: MODE_GEMGRAB,     # 슬롯 1 — 젬그랩
    2: MODE_SHOWDOWN,    # 슬롯 2 — 쇼다운
    3: MODE_BRAWLBALL,   # 슬롯 3 — 브롤볼
    4: MODE_BOUNTY,      # 슬롯 4 — 바운티
    5: MODE_SHOWDOWN,    # 슬롯 5 — 듀오 쇼다운
    6: MODE_HEIST,       # 슬롯 6 — 하이스트
    7: MODE_ROBORUMBLE,  # 슬롯 7 — 로보 럼블
    8: MODE_BOSSFIGHT,   # 슬롯 8 — 보스전
}


def _settings():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def battle_server_endpoint():
    """배틀 서버 접속 IP와 포트. 환경변수 > config.json > 기본값."""
    settings = _settings()
    ip = os.environ.get('BATTLE_SERVER_IP') or settings.get('BattleServerIp', '127.0.0.1')
    port = int(os.environ.get('BATTLE_SERVER_PORT') or settings.get('BattleServerPort', 1337))
    return ip, port


def encode_vint(data, rotate=True):
    final = b''
    if data == 0:
        return b'\x00'
    data = (data << 1) ^ (data >> 31)
    first = True
    while data:
        b = data & 0x7f
        if data >= 0x80:
            b |= 0x80
        if rotate and first:
            rotate = False
            lsb = b & 0x1
            msb = (b & 0x80) >> 7
            b >>= 1
            b = b & ~0xC0
            b = b | (msb << 7) | (lsb << 6)
        final += b.to_bytes(1, 'big')
        data >>= 7
    return final


def player_sid(battle_id, slot=0):
    return battle_id * 100 + slot


def register_session(sid, mode_id, battle_id, player_count=1):
    """로비 -> C# 배틀 서버 UDP 세션 등록 (로컬 127.0.0.1:1337)."""
    _, port = battle_server_endpoint()
    high = (sid >> 32) & 0xFFFFFFFF
    low = sid & 0xFFFFFFFF
    payload = struct.pack('>iih', high, low, REGISTRATION_MARKER)
    payload += encode_vint(mode_id) + encode_vint(battle_id) + encode_vint(player_count)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload, ('127.0.0.1', port))
        sock.close()
        print(f'[INFO] Battle session registered -> 127.0.0.1:{port} sid={sid} mode={mode_id} battle={battle_id} players={player_count}')
        return True
    except Exception as error:
        print(f'[ERROR] Battle session registration failed: {error}')
        return False


def start_battle(client, player, map_slot=1):
    """배틀 시작 처리: 세션 등록 후 24109 TeamGameStartingData 발송."""
    mode_id = MAP_INDEX_TO_MODE.get(map_slot, MODE_BRAWLBALL)
    battle_id = random.randint(1, 21474835)
    sid = player_sid(battle_id, 0)
    player_count = 6 if mode_id in (MODE_GEMGRAB, MODE_BRAWLBALL, MODE_HEIST, MODE_BOUNTY) else (10 if mode_id == MODE_SHOWDOWN else 1)

    register_session(sid, mode_id, battle_id, player_count)

    ip, port = battle_server_endpoint()

    from Protocol.Messages.Server.TeamGameStartingDataMessage import TeamGameStartingDataMessage
    try:
        from Protocol.Messages.Server.BattleTestMessage import BattleTestMessage
        BattleTestMessage(client, player, 0).send()
    except Exception:
        pass

    TeamGameStartingDataMessage(
        client, player,
        battle_id=battle_id, sid=sid, ip=ip, udp_port=port,
        mode_id=mode_id, map_id=getattr(player, 'map_id', 7), player_count=player_count
    ).send()
    print(f'[INFO] Battle {battle_id} started for player {player.ID} -> {ip}:{port}')
    return battle_id
