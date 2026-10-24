from ByteStream.Writer import Writer

class AllianceWarMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24776
        self.player = player

    def encode(self):
        # Most of the comments have been taken from PhoenixFire's structure
        self.writeLong(self.player.club_id) # AllianceID
        self.writeVInt(0) # ?

        # This may look like bad code, but I'm just trying to make it easier!
        clubMaps = [{"LocationID": 1}]
        self.writeVInt(len(clubMaps)) # Alliance War Maps Count
        for map in clubMaps:
            # AllianceWarNode::encode
            self.writeVInt(0)
            self.writeVInt(map.get("Index", 1)) # EventIndex
            self.writeVInt(0)
            self.writeVInt(map.get("SpriteID", 1)) # Club Wars SpriteID (Little ghost thingies from v20)
            self.writeDataReference(15, map["LocationID"]) # Event
            self.writeVInt(map.get("NodeState", 0)) # NodeState
            self.writeVInt(map.get("Timer", 0)) # Time left
            self.writeVInt(0) # Current Star Number (left side)

            self.writeArrayVint(map.get("Modifiers", [])) # Event Modifiers?

        self.writeVInt(0) # War Fractions Count
        for x in range(0):
            self.writeVInt(x + 1 if x != 3 else 1) # Club Wars SpriteID
            self.writeVInt(x) # Index