from ByteStream.Reader import Reader
from Protocol.LogicCommandManager import LogicCommandManager

class EndClientTurnMessage(Reader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.client = client
        self.player = player
        self.tick: int = 0
        self.checksum: int = 0
        self.commands: list = []

    def decode(self):
        self.readVInt()
        self.tick = self.readVInt()
        self.checksum = self.readVInt()

        for x in range(self.readVInt()): # Commands Count = self.readVInt() in this case
            commandID = self.readVInt()
            self.commands.append({"id": commandID})

            if LogicCommandManager.commandExists(commandID):
                if LogicCommandManager.isServerToClient(commandID): continue
                command = LogicCommandManager.createCommandByType(commandID)
                if command:
                    self.commands[x]["cls"] = command
                    command.decode(self)
                    print(f"CommandID: {commandID}, {command.__name__} handled!")
                else:
                    # Attempt to decode LogicCommand, a more proper reimplementation of Commands will come soon.
                    self.readVInt()
                    self.readVInt()
                    self.readLogicLong()
                    print(f"CommandID: {commandID}, {LogicCommandManager.getCommandName(commandID)} unhandled!")
            else:
                print(f"CommandID: {commandID} unhandled!")

    def process(self, db):
        if not self.commands: return

        for cmd in self.commands:
            if "cls" not in cmd: return

            if hasattr(cmd["cls"], "process"):
                print(cmd["cls"].__class__.__name__)
                cmd["cls"].process(self, db)
