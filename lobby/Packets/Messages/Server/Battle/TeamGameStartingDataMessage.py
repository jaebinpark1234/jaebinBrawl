from Utils.Writer import Writer


class TeamGameStartingDataMessage(Writer):
    """
    24109 — TeamGameStartingData (배틀 진입 핸드셰이크).

    로비(TCP 9339)가 배틀 시작을 알릴 때 클라이언트에게 배틀 서버 접속 정보를 전달한다:
      - 배틀 서버 IP (C# 배틀 서버가 떠 있는 호스트; docker-compose에서는 battle 컨테이너명)
      - 배틀 서버 UDP 포트 (기본 1337)
      - sid (세션 ID; battle_id * 100 + 슬롯 — lobby/Logic/BattleSessions.py 참고)
      - 모드/맵/인원

    ⚠ 이 인코딩은 v26 클라이언트 빌드별로 필드 순서가 다를 수 있어 '연결 가이드' 성격이다.
      클라이언트가 24109를 다르게 파싱하면 이 파일의 encode() 순서를 해당 빌드에 맞춰
      조정하면 되고, 배틀 서버 자체는 sid 기반이라 이 패킷 내용과 무관하게 동작한다.
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
        self.writeVint(0)                 # Unknown / tick
        self.writeString(self.ip)         # 배틀 서버 IP (UDP)
        self.writeVint(self.udp_port)     # 배틀 서버 UDP 포트
        self.writeInt(0)                  # HighID
        self.writeInt(self.sid & 0xFFFFFFFF)          # LowID 자리에 sid 하위 32비트
        self.writeInt((self.sid >> 32) & 0xFFFFFFFF)  # sid 상위 32비트 (UDP sid 복원용)
        self.writeVint(self.player_count) # 방 인원
        self.writeScId(15, self.map_id)   # MapID (SCID 15)
        self.writeVint(self.mode_id)      # 배틀 모드 ID (C# BattleModeRegistry 참고)
        self.writeVint(self.battle_id)    # 배틀 ID (같은 팀원 전원 동일)
        self.writeVint(0)                 # Reserved
        print(f"[INFO] TeamGameStartingData sent: battle={self.battle_id} sid={self.sid} -> {self.ip}:{self.udp_port} (mode {self.mode_id})")