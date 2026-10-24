from Utils.Writer import Writer
from Logic.BattleLog import load_battle_log


class BattleLogMessage(Writer):
    """
    23458 — Battle Log.

    Database/BattleLog/<low_id>.json 에 쌓인 전적을 클라이언트로 돌려준다.
    AskProfileMessage(14113) 처리 시 함께 전송된다.
    """

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 23458
        self.player = player

    def encode(self):
        entries = load_battle_log(self.player)

        self.writeBoolean(True)          # Battle log enabled
        self.writeVint(len(entries))     # Entry count

        for entry in entries:
            self.writeVint(0)                     # ??? (원본 유지)
            self.writeVint(entry.get('time', 0))  # 기록 생성 시각 (unix)
            self.writeVint(entry.get('battleType', 1))      # 1 = Normal, 2 = Crash, 3 = Survived
            self.writeVint(entry.get('trophiesResult', 0))  # 트로피 증감 결과
            self.writeVint(entry.get('battleTime', 120))    # 배틀 시간(초)
            self.writeUInt8(0)                    # 0 = Power Play, 1 = Friendly, 2 = Championship
            self.writeScId(15, entry.get('map', 0))         # Map SCID
            self.writeVint(entry.get('result', 0))          # 승/패/무 (클라이언트 보고 결과)
            self.writeVint(0)                     # ???

            self.writeInt(0)
            self.writeInt(0)

            players = entry.get('players', 0) or 1
            self.writeVint(players)               # 플레이어 배열 크기
            self.writeUInt8(1)

            # 본인 엔트리 (팀원/상대 확장은 각 플레이어 블록 반복으로)
            self.writeVint(0)
            self.writeUInt8(entry.get('team', 0))
            self.writeVint(0)
            self.writeUInt8(0)
            self.writeVint(0)

        print("[INFO] Message BattleLogMessage has been sent.")