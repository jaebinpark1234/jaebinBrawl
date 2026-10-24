import json
from sys import settrace

class Config:
    def create_config():
        """
        config.json 기본값 — '진짜 브롤식 육성 밸런스' (무한 재화 폐기).
        - 신규 유저: 골드 200 / 보석 30 / 티켓·스타포인트·상자 0 / 트로피 0
        - 쉘리(ID 0)만 해금, 나머지는 상자에서 획득
        - 파워 레벨 1 시작, PP+골드로 레벨업 (LogicUpgradeBrawler.py)
        """
        settings = {
            # ── 시작 재화 (입문용 소량) ──
            "Gems": 30,
            "Gold": 200,
            "Tickets": 0,
            "Starpoints": 0,
            "BrawlBoxTokens": 0,
            "BigBoxTokens": 0,
            # ── 육성 ──
            "BrawlerTrophies": 0,
            "BrawlerTrophiesForRank": 0,
            "BrawlerPowerLevel": 1,
            "BrawlerUpgradePoints": 0,
            "Trophies": 0,
            "ExperiencePoints": 0,
            "MaximumExperience": 145630,
            "TutorialState": 3,
            "ThemeID": 12,
            "Region": "RO",
            "SupportedContentCreator": "재빈브롤",
            "DoubleTokenEvent": "false",
            "CoinShowerEvent": "false",
            # ── 서버 운영 ──
            "ShowPacketsInLog": False,
            "Maintenance": False,
            "MaintenanceTime": 3600,
            "Patch": False,
            "PatchUrl": "",
            "UpdateUrl": "https://github.com/jaebinpark1234/jaebinBrawl",
            # ── 통합 배틀 서버 연동 ──
            "OnlineBattle": True,        # 온라인 배틀(UDP 1337) 라우팅 on/off
            "BattleServerIp": "127.0.0.1",
            "BattleServerPort": 1337
        }

        with open('config.json', 'w') as config_file:
            json.dump(settings, config_file)

    def GetValue():
        config_settings = {}
        Config_file = open('config.json', 'r')
        config_values = Config_file.read()

        config_settings = json.loads(config_values)
        return config_settings