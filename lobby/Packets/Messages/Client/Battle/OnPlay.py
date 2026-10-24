from Packets.Messages.Server.OutOfSyncMessage import OutOfSyncMessage
from Packets.Messages.Server.Battle.BattleTestMessage import BattleTestMessage

from Utils.Reader import BSMessageReader
from Utils.Config import Config
from Logic.BattleSessions import BattleSessions


class OnPlay(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client


    def decode(self):
        self.read_Vint()
        self.CardID = self.read_Vint()

        self.read_Vint()
        self.MapIndex = self.read_Vint()

        print(self.CardID, self.MapIndex)

    def process(self):
        if self.MapIndex in [1, 3, 4]:
            self.player.mmplayers = 6
        if self.MapIndex in [2, 5]:
            self.player.mmplayers = 10
        if self.MapIndex == 6:
            self.player.mmplayers = 6
        else:
            self.player.mmplayers = 6  # 알 수 없는 이벤트 맵도 3v3(6인) 기본 — 쇼다운(2,5)은 10인

        # ── 온라인 배틀 라우팅 (config.json 의 "OnlineBattle") ──────────────
        # 팀방에 있으면: 방 멤버 전원에게 같은 battle_id의 세션을 배정/등록하고
        #                TeamGameStartingDataMessage(24109)로 UDP 접속 정보를 브로드캐스팅.
        # 팀방이 아니면: 솔로 세션을 등록하고 본인에게만 24109 전송.
        # 어떤 오류가 나도 기존 오프라인 연습(20405)으로 폴백한다.
        if Config.GetValue().get('OnlineBattle', False):
            try:
                if self.player.room_id:
                    # 팀방: 방장 시작 = 즉시 시작 (멤버 전원 브로드캐스팅)
                    BattleSessions.start_team_battle(self.client, self.player, self.MapIndex)
                else:
                    # 일반 매칭: 15초 안에 정원이 안 차면 AI 봇 자동 충원 (Logic/Matchmaking.py)
                    from Logic.Matchmaking import Matchmaking
                    Matchmaking.enqueue(self.client, self.player, self.MapIndex)
                return
            except Exception as error:
                print(f'[ERROR] Online battle start failed, falling back to offline practice: {error}')

        BattleTestMessage(self.client, self.player, 0).send()
        #battle = LogicBattle(self.client, self.player)
        #battle.start()
