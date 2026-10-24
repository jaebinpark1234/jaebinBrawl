from Utils.Writer import Writer
from Database.DatabaseManager import DataBase

class AddableFriendsMessage(Writer):

    def __init__(self, client, player, players):
        super().__init__(client)
        self.id = 20199
        self.player = player
        self.players = players

    def encode(self):
        self.indexOfPlayer = 1
        
        self.writeInt(len(self.players)) # Playera Count
        for player in self.players:
            if player["lowID"] == self.player.low_id:
                self.indexOfPlayer = self.players.index(player) + 1
        
            self.writeInt(0) # Games Played Together Recently

            self.writeInt(0)  # HighID
            self.writeInt(player["lowID"])  # LowID

            self.writeString()
            self.writeString()
            self.writeString()
            self.writeString()
            self.writeString()
            self.writeString()


            self.writeInt(player.get('trophies', 0))  # Friend state 0 = friend, 1 = not friend, 2 = request sent, 3 = you have an invite from him??, 4 = friend list
            self.writeInt(4)
            self.writeInt(0)
            self.writeInt(0)
            self.writeInt(0)
        
            if player.get("clubID", 0) != 0:
                try:
                    DataBase.loadClub(self, player["clubID"])
                    self.writeBoolean(True)  # Is in club
                    self.writeInt(0)
                    self.writeInt(0)
                    self.writeInt(0)
                    self.writeString(getattr(self, 'clubName', '재빈브롤'))
                    self.writeInt(0)
                    self.writeInt(0)
                except Exception:
                    self.writeBoolean(False)
            else:
                self.writeBoolean(False)  # Is in club
            
            self.writeString()
            self.writeInt(0)
            
            self.writeBoolean(True)  # ?? is a player?
        
            self.writeString(player.get('name', 'Player'))
            self.writeVint(100)
            self.writeVint(28000000 + player.get("profileIcon", 0))
            self.writeVint(43000000 + player.get("namecolor", 0))

    