from ByteStream.Writer import Writer
from Logic.BattleLog import load_battle_log


class BattleLogMessage(Writer):
    """
    23458 — Battle Log Message.
    """

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 23458
        self.player = player

    def encode(self):
        entries = load_battle_log(self.player)

        self.writeBoolean(True)                  # Battle log enabled
        self.writeVInt(len(entries))             # Entry count

        for entry in entries:
            self.writeVInt(0)
            self.writeVInt(entry.get('time', 0))
            self.writeVInt(entry.get('battleType', 1))
            self.writeVInt(entry.get('trophiesResult', 0))
            self.writeVInt(entry.get('battleTime', 120))
            self.writeByte(0)
            self.writeDataReference(15, entry.get('map', 7))
            self.writeVInt(entry.get('result', 0))
            self.writeVInt(0)

            self.writeInt(0)
            self.writeInt(0)

            players = entry.get('players', 6) or 1
            self.writeVInt(players)
            self.writeByte(1)

            self.writeVInt(0)
            self.writeByte(entry.get('team', 0))
            self.writeVInt(0)
            self.writeByte(0)
            self.writeVInt(0)

        print(f"[INFO] BattleLogMessage sent for player {self.player.ID} ({len(entries)} entries)")
