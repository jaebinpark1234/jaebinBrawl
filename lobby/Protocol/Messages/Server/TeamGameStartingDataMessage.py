from ByteStream.Writer import Writer


class TeamGameStartingDataMessage(Writer):
    """
    24109 — TeamGameStartingData (배틀 진입 핸드셰이크).
    로비(TCP 9339)가 배틀 시작 시 클라이언트에게 C# 배틀 서버 접속 정보를 전달한다.
    """

    def __init__(self, client, player, battle_id, sid, ip, udp_port, mode_id, map_id, player_count):
        super().__init__(client)
        self.id = 24109
        self.player = player
        self.battle_id = battle_id
        self.sid = sid
        self.ip = ip
        self.udp_port = udp_port
        self.mode_id = mode_id
        self.map_id = map_id
        self.player_count = player_count

    def encode(self):
        self.writeVInt(0)                                # Unknown / tick
        self.writeString(self.ip)                        # 배틀 서버 IP (UDP)
        self.writeVInt(self.udp_port)                    # 배틀 서버 UDP 포트
        self.writeInt(0)                                 # HighID
        self.writeInt(self.sid & 0xFFFFFFFF)             # LowID (sid 하위 32비트)
        self.writeInt((self.sid >> 32) & 0xFFFFFFFF)     # sid 상위 32비트
        self.writeVInt(self.player_count)                # 인원
        self.writeDataReference(15, self.map_id)         # Map SCID
        self.writeVInt(self.mode_id)                     # 배틀 모드 ID
        self.writeVInt(self.battle_id)                   # 배틀 ID
        self.writeVInt(0)                                # Reserved
        print(f"[INFO] TeamGameStartingData sent: battle={self.battle_id} sid={self.sid} -> {self.ip}:{self.udp_port} (mode {self.mode_id})")
