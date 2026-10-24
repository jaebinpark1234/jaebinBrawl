from ByteStream.Writer import Writer

class BattleEndMessage(Writer):
    def __init__(self, client, player, gamemode: int, result: int, players: list):
        super().__init__(client)
        self.id = 23456
        self.player  = player
        self.gamemode    = gamemode
        self.result  = result
        self.players = players

    def encode(self):
        # Mostly taken from Icaro (IsaaSooBarr) as the comments are quite useful for everyone
        self.writeVInt(self.gamemode)  # Battle End Game Mode, 0 = 3vs3, 2 = Showdown, 3 = Robo Rumble, 4 = Big Game, 5 = Duo Showdown, 6 = Boss Fight
        self.writeVInt(self.result)  # Result (Victory/Defeat/Draw/Rank Score)
        self.writeVInt(0)  # Tokens Gained
        self.writeVInt(0)  # Trophies Result
        self.writeVInt(0)  # Power Play Points Gained
        self.writeVInt(0)  # Doubled Tokens
        self.writeVInt(0)  # Double Token Event
        self.writeVInt(0)  # Token Doubler Remaining
        self.writeVInt(0)  # Big Game/Robo Rumble Time and Boss Fight Level Cleared
        self.writeVInt(0)  # Epic Win Power Play Points Gained
        self.writeVInt(0)  # Championship Level Passed
        self.writeVInt(0)  # Challenge Reward Type (0 = Star Points, 1 = Star Tokens)
        self.writeVInt(0)  # Challenge Reward Amount
        self.writeVInt(0)  # Championship Losses Left
        self.writeVInt(0)  # Championship Maximum Losses
        self.writeVInt(0)  # Coin Shower Event
        self.writeVInt(0)  # Underdog Trophies
        # Maybe here I could write a few uint8s... but not very ideal
        self.writeVInt(
            32)  # Battle Result Type ((-16)-(-1) = Power Play Battle End, 0-15 = Practice and Championship Battle End, 16-31 = Matchmaking Battle End, 32-47 = Friendly Game Battle End, 48-63  = Spectate and Replay Battle End, 64-79 = Championship Battle End)
        self.writeVInt(0)  # Championship Challenge Type
        self.writeVInt(0)  # Championship Cleared and Beta Quests

        # Players Array
        self.writeVInt(len(self.players))  # Players
        for hero in self.players:
            team: int = 0
            if hero["isPlayer"] == 1 and hero["team"] == 1: team += 1
            if hero["team"] != self.players[0]["team"]: team += 2
            self.writeVInt(team)  # Player Team and Star Player Type
            self.writeDataReference(*hero["id"])  # Player Brawler
            self.writeDataReference(*hero["skin"])  # Player Skin
            self.writeVInt(0)  # Brawler Trophies
            self.writeVInt(0)  # Player Power Play Points
            self.writeVInt(1)  # Brawler Power Level
            self.writeBoolean(hero["isPlayer"] == 1)  # Player HighID and LowID Array
            if hero["isPlayer"] == 1:
                self.writeLong(self.player.ID)
            self.writeString(hero["name"])  # Player Name
            self.writeVInt(0)  # Player Experience Level
            self.writeVInt(28000000)  # Player Profile Icon
            self.writeVInt(43000000)  # Player Name Color

        # Experience Array
        self.writeVInt(2)  # Count
        for x in range(1):
            self.writeVInt(0)  # Normal Experience ID
            self.writeVInt(0)  # Normal Experience Gained
            self.writeVInt(8)  # Star Player Experience ID
            self.writeVInt(0)  # Star Player Experience Gained

        # Rank Up and Level Up Bonus Array
        self.writeVInt(0)  # Count

        # Trophies and Experience Bars Array
        self.writeVInt(2)  # Count
        for x in range(1):
            self.writeVInt(1)  # Trophies Bar Milestone ID
            self.writeVInt(0)  # Brawler Trophies
            self.writeVInt(0)  # Brawler Trophies for Rank
            self.writeVInt(5)  # Experience Bar Milestone ID
            self.writeVInt(0)  # Player Experience
            self.writeVInt(0)  # Player Experience for Level

        self.writeDataReference(28, 0)  # Player Profile Icon
        self.writeBoolean(False)  # Play Again Entry