from ByteStream.Writer import Writer

class LeaderboardMessage(Writer):

    def __init__(self, client, player, type, brawler, regional):
        super().__init__(client)
        self.id = 24403
        self.player = player
        self.leaderboardType: int = type
        self.brawler: list[int] = brawler
        self.isRegional: bool = regional

    def encode(self):
        print(self.leaderboardType)
        self.writeVInt(self.leaderboardType)
        self.writeVInt(0)
        self.writeDataReference(*self.brawler)
        self.writeString(self.player.region if self.isRegional else None)

        self.writeVInt(len(self.player.leaderboardData))
        for entry in self.player.leaderboardData:
            self.writeLogicLong(entry["ID"])
            self.writeVInt(1)
            self.writeVInt(entry["Trophies"])

            self.writeBooleanTest(self.leaderboardType in [0, 1])
            if self.leaderboardType in [0, 1]:
                self.writeString() # club name
                self.writeString(entry['Name'])

                self.writeVInt(9)
                self.writeVInt(28000000 + entry['ProfileIcon'])
                self.writeVInt(43000000 + entry['NameColor'])
                self.writeVInt(0)

            self.writeBooleanTest(self.leaderboardType == 2)
            if self.leaderboardType == 2:
                self.writeString(entry['Name'])
                self.writeVInt(len(entry['Members']))
                self.writeDataReference(8, entry['BadgeID'])

        self.writeVInt(0)
        self.writeVInt(0) # Index
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeString(self.player.region)