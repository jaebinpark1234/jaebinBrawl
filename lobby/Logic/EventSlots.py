import time

class EventSlots:
    # ── 이벤트 전면 개방 (트로피 제한 0) ─────────────────────────────────────
    # 서버는 이벤트 슬롯에 트로피 잠금을 걸지 않는다 — 신규 계정(트로피 0)도
    # 쇼다운·브롤볼·젬그랩 등 슬롯의 모든 이벤트를 즉시 플레이할 수 있다.
    # 잠금 요구 트로피는 클라이언트 csv(locations.csv) 쪽 값이므로 서버에서
    # 별도 필터를 두지 않는 한 0트로피에서 전부 열려 있다.
    Timer = 86399

    maps = [
        # Status = [3 = Nothing, 2 = Star Token, 1 = New Event]
        {
            'ID': 7,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        {
            'ID': 32,
            'Status': 2,
            'Ended': False,
            'Modifier': 2,
            'Tokens': 10
        },

        {
            'ID': 17,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        {
            'ID': 0,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        {
            'ID': 38,
            'Status': 2,
            'Ended': False,
            'Modifier': 2,
            'Tokens': 10
        },

        {
            'ID': 24,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        {
            'ID': 21,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 2
        },

        {
            'ID': 97,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # ── 주말 특별 이벤트 슬롯 (항상 활성화 — 트로피 0부터 플레이 가능) ──
        # 맵 ID는 AskForBattleEndMessage의 결과 분기와 맞춘 값:
        #   로보 럼블 27/29/39/68 · 보스전 57/67/133 · 빅 게임 21/30/65/66/119/120
        {
            'ID': 27,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        {
            'ID': 57,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        },

        # 시즌 이벤트(선물 훔치기) 슬롯.
        # TODO: v26 클라이언트 locations.csv에 선물 훔치기 전용 맵 ID가 있는지 확인 후
        #       교체. 당장은 알려진 맵 ID(7)를 재사용해 슬롯이 항상 열려 있게 유지한다.
        {
            'ID': 7,
            'Status': 2,
            'Ended': False,
            'Modifier': 0,
            'Tokens': 10
        }

    ]