from ByteStream.Writer import Writer

class LogicSetSupportedCreatorCommand(Writer):

    def encode(self):
        self.writeVInt(1)
        self.writeString(self.player.content_creator)
        self.writeVInt(1)

    def getCommandType(self) -> int:
        return 215
