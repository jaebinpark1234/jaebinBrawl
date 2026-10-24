import time

class EventSlots:
    # ── v26.184 순정 공식 맵 슬롯 매핑 ────────────────────────────────────
    # v26.184 클라이언트 locations.csv 및 공식 서버(PhoenixFire6934)와 100% 일치
    # 비정규 맵 ID나 비표준 모디파이어를 배제하여 클라이언트 C++ 메모리 크래시(튕김) 원천 방지
    Timer = 86399

    maps = [
        # Slot 1: 젬 그랩 (Mine - Hard Rock Mine)
        {
            'ID': 7,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 2: 쇼다운 (Default - Feast or Famine)
        {
            'ID': 32,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
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

        # Slot 5: 브롤볼 (Pinhole Punt - 23)
        {
            'ID': 23,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 6: 시즈 팩토리 (Bot Drop - 24)
        {
            'ID': 24,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # Slot 7: 보스전 / 빅 게임 (21)
        {
            'ID': 21,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        }
    ]
