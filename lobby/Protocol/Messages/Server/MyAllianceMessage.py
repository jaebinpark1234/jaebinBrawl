from ByteStream.Writer import Writer
from Files.CsvLogic.Regions import Regions

class MyAllianceMessage(Writer):
    def __init__(self, client, player, club_data):
        super().__init__(client)
        self.id = 24399
        self.player = player
        self.club_data = club_data

    def encode(self):
        self.writeVInt(0) # Online Club Members (Unused, was used in soft-launch versions)
        self.writeBoolean(self.player.club_id != 0) # Is in Club

        if self.player.club_id != 0:
            self.writeDataReference(25, self.player.club_role) # Member Role

            self.writeLong(self.club_data['ID'])
            self.writeString(self.club_data['Name'])
            self.writeDataReference(8, self.club_data['BadgeID'])
            self.writeVInt(self.club_data['Type'])
            self.writeVInt(len(self.club_data['Members']))
            self.writeVInt(self.club_data['Trophies'])
            self.writeVInt(self.club_data['RequiredTrophies'])
            self.writeDataReference(0, 0)
            self.writeString(Regions().get_region_string(self.club_data['Region']))
            self.writeVInt(0)
            self.writeVInt(self.club_data['FamilyFriendly'])