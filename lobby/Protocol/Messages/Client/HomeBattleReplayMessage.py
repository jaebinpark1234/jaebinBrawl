from ByteStream.Reader import Reader
from Protocol.Messages.Server.BattleLogMessage import BattleLogMessage


class HomeBattleReplayMessage(Reader):
    """14114 — Request Battle Log"""

    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        pass

    def process(self, db):
        BattleLogMessage(self.client, self.player).send()
