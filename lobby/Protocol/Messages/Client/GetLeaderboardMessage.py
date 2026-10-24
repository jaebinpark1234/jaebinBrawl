from ByteStream.Reader import Reader
from Protocol.Messages.Server.LeaderboardMessage import LeaderboardMessage

class GetLeaderboardMessage(Reader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client
        self.isRegional: bool = False
        self.brawler: list[int] = []
        self.type: int = 0

    def decode(self):
        self.isRegional = self.readBool()
        self.brawler = self.readDataReference()
        self.type = self.readVInt()

    def process(self, db):
        if self.type == 1:
            self.player.leaderboardData = db.load_all_players_sorted({}, 'Trophies')
            LeaderboardMessage(self.client, self.player, self.type, self.brawler, self.isRegional).send()

        elif self.type == 0: # Brawlers
            self.player.leaderboardData = db.load_all_players_sorted({}, 'BrawlersTrophies', str(self.brawler[1]))
            LeaderboardMessage(self.client, self.player, self.type, self.brawler, self.isRegional).send()

        elif self.type == 2:
            self.player.leaderboardData = db.load_all_clubs_sorted({}, 'Trophies')
            LeaderboardMessage(self.client, self.player, self.type, self.brawler, self.isRegional).send()