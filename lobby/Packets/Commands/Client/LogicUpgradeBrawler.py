from Database.DatabaseManager import DataBase

from Utils.Reader import BSMessageReader

# ── 정석 육성 트리: 레벨업 비용 (파워포인트, 골드) ───────────────────────────
# 현재 레벨 → 다음 레벨 업그레이드 비용. 브롤스타즈 원작 밸런스.
UPGRADE_COSTS = {
    1: (20, 20),      # 파워 1 → 2
    2: (30, 35),      # 파워 2 → 3
    3: (50, 75),      # 파워 3 → 4
    4: (80, 140),     # 파워 4 → 5
    5: (130, 290),    # 파워 5 → 6
    6: (200, 480),    # 파워 6 → 7
    7: (300, 800),    # 파워 7 → 8
    8: (440, 1250),   # 파워 8 → 9
}
MAX_POWER_LEVEL = 9


class Upgrade_Brawler(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.read_Vint()
        self.read_Vint()
        self.read_Vint()
        self.read_Vint()
        self.read_Vint()                  # csvID
        self.BrawlerID = self.read_Vint() # BrawlerID


    def process(self):
        brawler_id = str(self.BrawlerID)
        current_level = self.player.Brawler_level[brawler_id]

        # 최대 파워 레벨 체크
        if current_level >= MAX_POWER_LEVEL:
            print(f'[INFO] Upgrade denied: brawler {brawler_id} already at max power level {MAX_POWER_LEVEL}')
            return

        # 비용: (파워포인트, 골드)
        pp_cost, gold_cost = UPGRADE_COSTS.get(current_level, (440, 1250))
        power_points = self.player.brawlers_upgradium[brawler_id]
        gold = self.player.gold

        # 파워포인트/골드 부족 시 거부 (무료 만렙 폐기)
        if power_points < pp_cost or gold < gold_cost:
            print(f'[INFO] Upgrade denied: brawler {brawler_id} needs {pp_cost} PP + {gold_cost} gold '
                  f'(have {power_points} PP, {gold} gold)')
            return

        # 지불 + 레벨업
        self.player.brawlers_upgradium[brawler_id] = power_points - pp_cost
        self.player.gold = gold - gold_cost
        self.player.Brawler_level[brawler_id] += 1

        DataBase.replaceValue(self, 'brawlersUpgradePoints', self.player.brawlers_upgradium)
        DataBase.replaceValue(self, 'gold', self.player.gold)
        DataBase.replaceValue(self, 'brawlerPowerLevel', self.player.Brawler_level)

        print(f'[INFO] Brawler {brawler_id} upgraded to power {self.player.Brawler_level[brawler_id]} '
              f'(-{pp_cost} PP, -{gold_cost} gold)')