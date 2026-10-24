"""
BattleSessions — 로비 ↔ C# 배틀 서버(UDP) 핸드셰이크 연동부.

역할:
  1. 배틀 시작 시 배틀 ID(battle_id)를 배정하고, 팀방 멤버 전원에게 각자의
     세션 ID(sid = battle_id * 100 + 슬롯)를 배정한다.
  2. C# 배틀 서버(Atrasis.Laser.Battle)로 UDP 등록 패킷을 먼저 보내
     세션의 게임 모드/소속 배틀을 미리 알려준다 (마커 0xFFFF).
  3. 팀방(TeamGameroom)에 있는 모든 멤버의 클라이언트에게
     TeamGameStartingDataMessage(24109)로 접속 정보(배틀 서버 IP/UDP 포트, sid)를
     브로드캐스팅한다 → 모두 같은 battle_id의 배틀 세션 그룹으로 진입한다.

C# 쪽 파싱은 battle/Atrasis.Laser.Battle/Program.cs 의 OnReceive/RegisterSession.
패킷 레이아웃(등록): [Int 0][Int sid][Short 0xFFFF][VInt modeId][VInt battleId][VInt playerCount]
"""

import os
import random
import socket
import struct

from tinydb import TinyDB, Query

from Utils.Config import Config

# ── C# BattleModeRegistry.cs 의 상수와 동일하게 유지할 것 ─────────────────────
# 정규 이벤트
MODE_GEMGRAB = 0
MODE_SHOWDOWN = 2        # 솔로 10인 / 듀오 5팀 10인
MODE_HEIST = 3
MODE_BOUNTY = 4
MODE_BRAWLBALL = 5       # ✅ 배틀 서버에 구현된 테스트 기반 모드
# 주말 특별 이벤트
MODE_ROBORUMBLE = 6
MODE_BOSSFIGHT = 7
MODE_BIGGAME = 8
# 기타 / 시즌 이벤트
MODE_LONESTAR = 11
MODE_TAKEDOWN = 12
MODE_PRESENTPLUNDER = 13

# 로비 → 배틀 서버 세션 등록 패킷 마커 (C# Program.RegistrationMarker)
REGISTRATION_MARKER = -1  # C#은 short로 0xFFFF를 읽는다 (= -1)

# 이벤트 슬롯(OnPlay의 MapIndex) → 배틀 모드 배정표.
# 미구현 모드로 배정되면 C# 레지스트리가 BrawlBall(테스트 기반)로 폴백하므로
# 세션이 크래시 나지 않는다. 새 모드 구현 후 이 표만 바꾸면 바로 적용된다.
MAP_INDEX_TO_MODE = {
    1: MODE_GEMGRAB,     # 슬롯 1 — 젬그랩
    2: MODE_SHOWDOWN,    # 슬롯 2 — 쇼다운 (10인)
    3: MODE_BRAWLBALL,   # 슬롯 3 — 브롤볼
    4: MODE_BOUNTY,      # 슬롯 4 — 바운티
    5: MODE_SHOWDOWN,    # 슬롯 5 — 듀오 쇼다운 (5팀 10인)
    6: MODE_HEIST,       # 슬롯 6 — 하이스트
    7: MODE_ROBORUMBLE,  # 슬롯 7 — 로보 럼블 (주말 이벤트)
    8: MODE_BOSSFIGHT,   # 슬롯 8 — 보스전 (주말 이벤트)
}


def _settings():
    """config.json 값 읽기. 구버전 config.json(새 키 없음)도 기본값으로 동작하게 .get 사용."""
    try:
        return Config.GetValue()
    except Exception:
        return {}


def battle_server_endpoint():
    """배틀 서버 접속점. 환경변수(BATTLE_SERVER_IP/BATTLE_SERVER_PORT)가 config.json보다 우선."""
    settings = _settings()
    ip = os.environ.get('BATTLE_SERVER_IP') or settings.get('BattleServerIp', '127.0.0.1')
    port = int(os.environ.get('BATTLE_SERVER_PORT') or settings.get('BattleServerPort', 1337))
    return ip, port


def encode_vint(data, rotate=True):
    """Utils/Writer.writeVint 와 동일한 알고리즘의 순수 함수 버전 (UDP 등록 패킷용)."""
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


def player_sid(battle_id, slot):
    """배틀 서버가 세션을 구분하는 sid. 같은 배틀의 멤버는 같은 battle_id를 공유한다."""
    return battle_id * 100 + slot


def register_session(sid, mode_id, battle_id, player_count, udp=None):
    """로비 → C# 배틀 서버 세션 등록 패킷 전송 (UDP)."""
    ip, port = battle_server_endpoint()
    payload = struct.pack('>iih', 0, sid, REGISTRATION_MARKER)
    payload += encode_vint(mode_id) + encode_vint(battle_id) + encode_vint(player_count)
    try:
        sock = udp or socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload, (ip, port))
        if udp is None:
            sock.close()
        print(f'[INFO] Battle session registered -> {ip}:{port} sid={sid} mode={mode_id} battle={battle_id} players={player_count}')
        return True
    except Exception as error:
        print(f'[ERROR] Battle session registration failed ({ip}:{port}): {error}')
        return False


def load_room_members(room_id):
    """팀방 멤버 low_id 목록 (방장 먼저). Database/Gameroom/gameroom.db 직접 조회."""
    db = TinyDB('Database/Gameroom/gameroom.db')
    query = Query()
    data = db.search(query.room_id == room_id)
    members = []
    if data:
        info = data[0]['info']
        entries = [value for key, value in info.items() if key not in ('mapID', 'useGadget', 'PlayerCount')]
        entries.sort(key=lambda e: -int(e.get('host', 0)))
        for entry in entries:
            members.append(int(entry.get('lowID', 0)))
    return members


def get_client_socket(low_id, player):
    """low_id → 접속 중인 클라이언트 소켓. 로그인(10101) 시 기록된 ClientDict를 사용한다."""
    clients = getattr(player, 'ClientDict', {}) or {}
    entry = clients.get('Clients', {}).get(str(low_id))
    if entry:
        return entry.get('SocketInfo')
    return None


def start_team_battle(client, player, map_index):
    """팀방에서 방장이 시작(OnPlay)했을 때: 멤버 전원을 같은 배틀로 브로드캐스팅."""
    room_id = player.room_id
    members = load_room_members(room_id)
    if not members:
        # 방 데이터가 이미 정리된 경우 → 솔로 배틀로 처리
        return start_solo_battle(client, player, map_index)

    mode_id = MAP_INDEX_TO_MODE.get(map_index, MODE_BRAWLBALL)
    # battle_id 상한: sid = battle_id * 100 + 슬롯이 int32(UDP 패킷 Int 필드)를 넘지 않게.
    battle_id = random.randint(1, 21474835)
    ip, port = battle_server_endpoint()

    for slot, low_id in enumerate(members):
        sid = player_sid(battle_id, slot)
        register_session(sid, mode_id, battle_id, len(members))

        member_socket = get_client_socket(low_id, player)
        if member_socket is None:
            print(f'[WARN] room member {low_id} socket not found; skipped')
            continue

        from Packets.Messages.Server.Battle.BattleTestMessage import BattleTestMessage
        from Packets.Messages.Server.Battle.TeamGameStartingDataMessage import TeamGameStartingDataMessage

        BattleTestMessage(member_socket, player, 0).send()
        TeamGameStartingDataMessage(
            member_socket, player,
            battle_id=battle_id, sid=sid, ip=ip, udp_port=port,
            mode_id=mode_id, map_id=player.map_id, player_count=len(members)
        ).send()

    print(f'[INFO] Team battle {battle_id} started: {len(members)} members, mode={mode_id}, map={player.map_id}')
    return battle_id


def start_solo_battle(client, player, map_index):
    """솔로(오프라인 연습 자리에 온라인 세션 연결) 배틀 시작."""
    mode_id = MAP_INDEX_TO_MODE.get(map_index, MODE_BRAWLBALL)
    battle_id = random.randint(1, 21474835)  # sid int32 오버플로 방지
    ip, port = battle_server_endpoint()
    sid = player_sid(battle_id, 0)

    register_session(sid, mode_id, battle_id, 1)

    from Packets.Messages.Server.Battle.BattleTestMessage import BattleTestMessage
    from Packets.Messages.Server.Battle.TeamGameStartingDataMessage import TeamGameStartingDataMessage

    BattleTestMessage(client, player, 0).send()
    TeamGameStartingDataMessage(
        client, player,
        battle_id=battle_id, sid=sid, ip=ip, udp_port=port,
        mode_id=mode_id, map_id=player.map_id, player_count=1
    ).send()
    return battle_id


class BattleSessions:
    """패킷 핸들러(OnPlay 등)에서 쓰기 편하게 감싼 래퍼."""

    @staticmethod
    def start_team_battle(client, player, map_index):
        return start_team_battle(client, player, map_index)

    @staticmethod
    def start_solo_battle(client, player, map_index):
        return start_solo_battle(client, player, map_index)