from ByteStream.Writer import Writer

class LobbyInfoMessage(Writer):
    def __init__(self, client, player, count):
        super().__init__(client)
        self.id = 23457
        self.player = player
        self.count = count

    def encode(self):
        self.writeVInt(self.count) # Players Online
        self.writeString("재빈브롤 v26")

        self.writeVInt(0) # Lobby Info Entry Count
