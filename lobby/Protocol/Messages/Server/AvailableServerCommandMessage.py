from ByteStream.Writer import Writer

class AvailableServerCommandMessage(Writer):

    def __init__(self, client, player, command):
        super().__init__(client)
        self.id = 24111
        self.player = player
        self.command = command

    def encode(self):
        if not self.command:
            print("[AvailableServerCommand::] Command must not be null")
        self.writeVInt(self.command.getCommandType(self))
        self.command.encode(self)
