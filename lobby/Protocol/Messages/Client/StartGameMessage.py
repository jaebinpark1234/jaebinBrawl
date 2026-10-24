from ByteStream.Reader import Reader
from Protocol.Messages.Server.TeamMessage import TeamMessage
from Protocol.Messages.Server.MatchMakingCancelledMessage import MatchMakingCancelledMessage
from Logic.Home.LogicEventData import LogicEventData

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
        except:
            self.player.map_id = 7

        MatchMakingCancelledMessage(self.client, self.player).send()
        TeamMessage(self.client, self.player).send()
