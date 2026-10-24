import time

class EventSlots:
    # ── 이벤트 전면 개방 (8개 슬롯 고정) ──────────────────────────────────
    # v26 클라이언트 UI는 슬롯이 정확히 8개(1~8번)로 고정되어 있습니다.
    # 8개를 초과하는 슬롯을 보내거나 동일 슬롯 번호가 중복되면 클라이언트가 즉시 크래시(튕김)됩니다.
    # 모든 이벤트는 트로피 0점부터 입장 가능합니다.
    Timer = 86399

    maps = [
        # Slot 1: 젬 그랩 (Hard Rock Mine)
        {
            'ID': 7,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 2: 쇼다운 (Feast or Famine)
        {
            'ID': 32,
            'Status': 2,
            'Ended': False,
            'Modifier': 2,
            'Tokens': 10
        },

        # Slot 3: 하이스트 (Safe Zone)
        {
            'ID': 17,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 4: 바운티 (Shooting Star)
        {
            'ID': 0,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 5: 브롤볼 (Backyard Bowl)
        {
            'ID': 38,
            'Status': 2,
            'Ended': False,
            'Modifier': 2,
            'Tokens': 10
        },

        # Slot 6: 시즈 팩토리 (Bot Drop)
        {
            'ID': 24,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 7: 주말 특별 이벤트 - 빅 게임 / 보스전 (21)
        {
            'ID': 21,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 8: 특별 이벤트 - 선물 훔치기 (97)
        {
            'ID': 97,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        }
    ]
