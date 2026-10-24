"""
Matchmaking — 15초 매치메이킹 봇 자동 충원 시스템.

사설 서버 특성상 동시 접속자가 적으면 매칭 대기열이 무한 대기하는 문제를 해결한다:

  1. OnPlay(14103)에서 팀방 없이 배틀을 시작하면 모드별 대기열에 들어간다.
  2. 백그라운드 스레드가 0.5초마다 대기열을 확인한다:
     - 정원(3v3 계열 6명, 쇼다운 10명 등)이 차면 즉시 시작.
     - 15초가 지나도 정원이 안 차면 부족한 슬롯을 AI 봇(봇 닉네임 + 브롤러/트로피)으로
       자동 백필하고 즉시 시작.
  3. 시작 시 실제 플레이어 전원에게 배틀 서버(UDP) 세션 등록 + 24109 전송.
     봇은 24109의 인원수(player_count)에 포함되어 클라이언트가 렌더링한다.
     (C# 배틀 서버의 세션은 실제 접속 플레이어의 sid에만 만든다.)

팀방(친선전)은 방장이 시작하는 즉시 배틀이므로 이 큐를 거치지 않는다.
"""

import random
import threading
import time

from Logic.BattleSessions import (
    MODE_GEMGRAB, MODE_SHOWDOWN, MODE_HEIST, MODE_BOUNTY, MODE_BRAWLBALL,
    MODE_ROBORUMBLE, MODE_BOSSFIGHT, MODE_BIGGAME,
    MODE_LONESTAR, MODE_TAKEDOWN, MODE_PRESENTPLUNDER,
    MAP_INDEX_TO_MODE, player_sid, register_session, battle_server_endpoint,
)

MATCH_TIMEOUT = 15.0      # 초 — 이 시간 안에 정원이 안 차면 봇으로 백필
SCAN_INTERVAL = 0.5       # 초 — 대기열 스캔 주기

# 모드별 정원. OnPlay의 mmplayers 규칙(3v3=6, 쇼다운=10) + 주말 이벤트 인원.
MODE_CAPACITY = {
    MODE_GEMGRAB: 6,
    MODE_BRAWLBALL: 6,
    MODE_HEIST: 6,
    MODE_BOUNTY: 6,
    MODE_SHOWDOWN: 10,     # 솔로 10인 / 듀오 5팀 10인
    MODE_ROBORUMBLE: 3,    # 협동 3인
    MODE_BOSSFIGHT: 3,     # 협동 3인
    MODE_BIGGAME: 4,       # 1 vs 3
    MODE_LONESTAR: 6,
    MODE_TAKEDOWN: 10,
    MODE_PRESENTPLUNDER: 6,
}

BOT_NAMES = [
    'Bot Alpha', 'Bot Bravo', 'Bot Charlie', 'Bot Delta', 'Bot Echo',
    'Bot Foxtrot', 'Bot Golf', 'Bot Hotel', 'Bot India', 'Bot Juliet',
    'Bot Kilo', 'Bot Lima', 'Bot Mike', 'Bot November', 'Bot Oscar',
]


class _ModeQueue:
    """한 게임 모드의 대기열 상태."""
    def __init__(self):
        self.lock = threading.Lock()
        self.players = {}   # low_id -> {'client': socket, 'player': Players, 'joined': ts}
        self.oldest = None  # 대기열에 처음 사람이 들어온 시각


class Matchmaking:
    _queues = {}            # mode_id -> _ModeQueue
    _class_lock = threading.Lock()
    _worker_started = False

    # ── 공개 API ──────────────────────────────────────────────────────────────

    @classmethod
    def enqueue(cls, client, player, map_index):
        """배틀 시작 요청(팀방 없는 OnPlay). 정원이 이미 차면 즉시 시작, 아니면 대기열."""
        mode_id = MAP_INDEX_TO_MODE.get(map_index, MODE_BRAWLBALL)
        capacity = MODE_CAPACITY.get(mode_id, 6)

        queue = cls._queues.setdefault(mode_id, _ModeQueue())
        with queue.lock:
            # 같은 플레이어가 다시 요청하면 갱신(중복 등록 방지)
            queue.players[player.low_id] = {'client': client, 'player': player, 'joined': time.time()}
            if queue.oldest is None:
                queue.oldest = time.time()
            full = len(queue.players) >= capacity

        cls._ensure_worker()

        if full:
            cls._start_queue(mode_id, reason='full')
            return {'started': True, 'waited': 0.0}
        return {'started': False, 'waited': 0.0}

    @classmethod
    def cancel(cls, player):
        """매칭 취소(CancelMatchmaking, 14106)."""
        for queue in cls._queues.values():
            with queue.lock:
                queue.players.pop(player.low_id, None)
                if not queue.players:
                    queue.oldest = None

    @classmethod
    def queue_size(cls, mode_id):
        queue = cls._queues.get(mode_id)
        if not queue:
            return 0
        with queue.lock:
            return len(queue.players)

    # ── 내부 ──────────────────────────────────────────────────────────────────

    @classmethod
    def _ensure_worker(cls):
        with cls._class_lock:
            if cls._worker_started:
                return
            cls._worker_started = True
            worker = threading.Thread(target=cls._worker, daemon=True)
            worker.start()

    @classmethod
    def _worker(cls):
        while True:
            time.sleep(SCAN_INTERVAL)
            now = time.time()
            for mode_id, queue in list(cls._queues.items()):
                with queue.lock:
                    if not queue.players:
                        queue.oldest = None
                        continue
                    capacity = MODE_CAPACITY.get(mode_id, 6)
                    waited = now - queue.oldest
                    if len(queue.players) >= capacity or waited >= MATCH_TIMEOUT:
                        # 대기열을 잠근 채 시작 정보를 넘긴다
                        entries = list(queue.players.values())
                        queue.players.clear()
                        queue.oldest = None
                    else:
                        continue
                # 락 밖에서 시작 (네트워크 I/O 포함)
                cls._start_with_backfill(mode_id, entries, capacity, waited)

    @classmethod
    def _start_queue(cls, mode_id, reason):
        queue = cls._queues[mode_id]
        with queue.lock:
            entries = list(queue.players.values())
            queue.players.clear()
            queue.oldest = None
        capacity = MODE_CAPACITY.get(mode_id, 6)
        cls._start_with_backfill(mode_id, entries, capacity, 0.0)

    @staticmethod
    def _make_bots(count):
        """부족한 슬롯을 채울 AI 봇 목록."""
        bots = []
        for i in range(count):
            bots.append({
                'name': random.choice(BOT_NAMES),
                'brawler': random.randint(0, 37),
                'trophies': random.randint(0, 100),
                'team': i % 2,  # 3v3: 블루/레드 교대, 쇼다운: 각자 전부
            })
        return bots

    @classmethod
    def _start_with_backfill(cls, mode_id, entries, capacity, waited):
        real = len(entries)
        bots = cls._make_bots(max(0, capacity - real))
        mode_name = {v: k for k, v in {
            'GemGrab': MODE_GEMGRAB, 'Showdown': MODE_SHOWDOWN, 'Heist': MODE_HEIST,
            'Bounty': MODE_BOUNTY, 'BrawlBall': MODE_BRAWLBALL, 'RoboRumble': MODE_ROBORUMBLE,
            'BossFight': MODE_BOSSFIGHT, 'BigGame': MODE_BIGGAME, 'LoneStar': MODE_LONESTAR,
            'Takedown': MODE_TAKEDOWN, 'PresentPlunder': MODE_PRESENTPLUNDER,
        }.items()}.get(mode_id, f'Mode{mode_id}')

        from Packets.Messages.Server.Battle.BattleTestMessage import BattleTestMessage
        from Packets.Messages.Server.Battle.TeamGameStartingDataMessage import TeamGameStartingDataMessage

        battle_id = random.randint(1, 21474835)  # sid int32 오버플로 방지
        ip, port = battle_server_endpoint()

        for slot, entry in enumerate(entries):
            sid = player_sid(battle_id, slot)
            register_session(sid, mode_id, battle_id, capacity)

            member_socket = entry['client']
            member_player = entry['player']
            if member_socket is None or member_player is None:
                continue
            try:
                BattleTestMessage(member_socket, member_player, 0).send()
                TeamGameStartingDataMessage(
                    member_socket, member_player,
                    battle_id=battle_id, sid=sid, ip=ip, udp_port=port,
                    mode_id=mode_id, map_id=member_player.map_id, player_count=capacity
                ).send()
            except Exception as error:
                print(f'[ERROR] match start packet failed for {entry["player"].low_id}: {error}')

        if bots:
            print(f'[INFO] Match {battle_id} ({mode_name}): {real} real + {len(bots)} AI bots '
                  f'(waited {waited:.1f}s) -> {ip}:{port}')
        else:
            print(f'[INFO] Match {battle_id} ({mode_name}): {real} real players (full) -> {ip}:{port}')
        return battle_id