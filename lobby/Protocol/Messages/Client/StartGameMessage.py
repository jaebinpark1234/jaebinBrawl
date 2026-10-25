from ByteStream.Reader import Reader
from Logic.Home.LogicEventData import LogicEventData
from Logic.BattleSessions import start_battle


class StartGameMessage(Reader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.readVInt()
        self.readVInt()
        self.readVInt()
        self.map_slot = self.readVInt()

    def process(self, db):
        try:
            self.player.map_id = LogicEventData.events[self.map_slot - 1].get("LocationID", 0)
        except Exception:
            self.player.map_id = 7

        print(f"[INFO] StartGameMessage: map_slot={self.map_slot}, map_id={self.player.map_id} -> starting battle session")
        start_battle(self.client, self.player, self.map_slot)
