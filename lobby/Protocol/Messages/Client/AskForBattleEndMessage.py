from ByteStream.Reader import Reader
from Protocol.Messages.Server.BattleEndMessage import BattleEndMessage

class AskForBattleEndMessage(Reader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client
        self.players: list = []

    def decode(self):
        self.result   = self.readVInt()
        self.unk      = self.readVInt()
        self.rank     = self.readVInt()
        self.mapID    = self.readDataReference()

        self.count    = self.readVInt()

        for player in range(self.count):
            self.players.append({'id': self.readDataReference(), 'skin': self.readDataReference(), 'team': self.readVInt(), 'isPlayer': self.readVInt(), 'name': self.readString()})


    def process(self, db):
        if self.player.status != 8: return
        if self.count not in [3, 6, 10]: return

        if self.rank != 0:
            if self.players[0]['team'] == self.players[1]['team']:
                self.type = 5
            else:
                self.type = 2
        else:
            self.type = 0

        BattleEndMessage(self.client, self.player, self.type, self.result, self.players).send()