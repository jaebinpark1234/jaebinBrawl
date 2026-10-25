from ByteStream.Writer import Writer


class BattleTestMessage(Writer):
    """20405 — BattleTestMessage"""

    def __init__(self, client, player, state=0):
        super().__init__(client)
        self.id = 20405
        self.player = player
        self.state = state

    def encode(self):
        self.writeInt(0)  # timer
        self.writeInt(1)  # Current player
        self.writeInt(6)  # Max players
        self.writeInt(1)  # Unknown
        self.writeString("Player")
        self.writeVInt(10)
