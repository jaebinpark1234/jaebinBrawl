from Packets.Messages.Server.Home.PlayerProfileMessage import PlayerProfileMessage
from Packets.Messages.Server.Battle.BattleLogMessage import BattleLogMessage
from Database.DatabaseManager import DataBase

from Utils.Reader import BSMessageReader


class AskProfileMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.high_id = self.read_int()
        self.low_id = self.read_int()


    def process(self):
        self.players = DataBase.getAllPlayers(self)
        if self.high_id == 0:
            PlayerProfileMessage(self.client, self.player, self.high_id, self.low_id, self.players).send()
            # 전투 기록도 함께 전송 (Logic/BattleLog.py 에 저장된 전적)
            try:
                BattleLogMessage(self.client, self.player).send()
            except Exception as error:
                print(f'[ERROR] BattleLogMessage send failed: {error}')
