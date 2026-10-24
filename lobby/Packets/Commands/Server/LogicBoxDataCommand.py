from random import *
from Database.DatabaseManager import DataBase
from Packets.Messages.Server.OutOfSyncMessage import OutOfSyncMessage
from Logic.Boxes import Boxes

from Utils.Writer import Writer

import random


class LogicBoxDataCommand(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24111
        self.player = player
        self.BoxData = Boxes.boxes

    def encode(self):
        # ── 박스 드롭 확률 (진짜 브롤식 육성 밸런스 — 맛깔나게 상향) ─────────────
        # 기존: Nothing 0.50 / Brawler 0.18 / Tickets 0.15 / Gems 0.09 / TokensDoubler 0.05
        # 새로: 브롤러 해금 2배 가까이 상향 + 꽝(OnlyPowerpoints) 축소.
        #  - 브롤러(Brawler) 0.35 : 상자에서 새 브롤러가 자주 나와 성취감 확보
        #  - 젬/토큰두블러 소폭 상향, 티켓 축소
        reward_list = ["Nothing", "Brawler", "Tickets", "Gems", "TokensDoubler"]
        reward_weights = [0.30, 0.35, 0.08, 0.12, 0.15]

        unlocked_brawlers = []
        unlockable_brawlers = []

        for brawlers_id in self.player.BrawlersUnlockedState:
            if self.player.BrawlersUnlockedState[brawlers_id] == 0:
                unlockable_brawlers.append(int(brawlers_id))
            elif self.player.BrawlersUnlockedState[brawlers_id] == 1 and self.player.Brawler_level[brawlers_id] != 9:
                unlocked_brawlers.append(int(brawlers_id))

        self.box_index = 0
        def get_id(id):
            if id == 5:  # Brawl Box
                return 10
            elif id == 4:  # Big Box
                self.box_index = 1
                return 12
            elif id == 3:  # Shop Mega Box
                self.box_index = 3
                DataBase.replaceValue(self, 'gems', self.player.gems - 80)
                return 11
            elif id == 1:  # Shop Big Box
                self.box_index = 2
                DataBase.replaceValue(self, 'gems', self.player.gems - 30)
                return 12
            elif id == 6:  # Trophy Road milestone reward
                # ── 트로피 로드 보상 개편 ──────────────────────────────────────
                # 기존 이벤트 해금 마일스톤 자리를 대형/메가 상자 교대 지급으로 교체.
                # 진척도(leagueReward)는 보상을 줄 때마다 +1 되어 다음 마일스톤으로.
                if self.player.trophy_road % 2 == 0:
                    self.box_index = 1  # Big Box
                    box_id = 12
                else:
                    self.box_index = 3  # Mega Box
                    box_id = 11
                self.player.trophy_road += 1
                DataBase.replaceValue(self, 'leagueReward', self.player.trophy_road)
                print(f'[INFO] Trophy road milestone {self.player.trophy_road - 1} claimed -> {"Mega" if box_id == 11 else "Big"} Box')
                return box_id

        self.box_skin_id = get_id(self.player.box_id)
        box_content = {"RewardType": "", "RewardCount": 1, "Gold": randint(self.BoxData[self.box_index]["Coins"][0], self.BoxData[self.box_index]["Coins"][1])}
        reward = choices(reward_list, weights=reward_weights, k=1)

        if reward[0] == "Brawler" and len(unlockable_brawlers) == 0:
            # 더 이상 해금할 브롤러가 없으면 브롤러 자리를 빼고 재추첨 (가중치도 같이 정렬)
            idx = reward_list.index("Brawler")
            reward_list.pop(idx)
            reward_weights.pop(idx)
            reward = choices(reward_list, weights=reward_weights, k=1)

        brawlers_rewarded = []
        # 전 브롤러가 파워 9(만렙)이면 PP 대상이 없다 — 빈 리스트 choice 방지
        choosed_brawler = choice(unlocked_brawlers) if unlocked_brawlers else 0

        # Brawler randomizer
        while len(brawlers_rewarded) != self.BoxData[self.box_index]["MaxUpgradePoints"]:
            if len(unlocked_brawlers) < self.BoxData[self.box_index]["MaxUpgradePoints"]:
                for i in range(len(unlocked_brawlers)):
                    brawlers_rewarded.append(unlocked_brawlers[i])
                break
            elif choosed_brawler not in brawlers_rewarded:
                brawlers_rewarded.append(choosed_brawler)
            else:
                choosed_brawler = choice(unlocked_brawlers)

        # Reward manager
        if reward[0] == "Brawler":
            box_content["RewardType"] = reward[0]
            if self.BoxData[self.box_index]["NewCharPosition"] == "Start":
                box_content["RewardCount"] = 1
            elif self.BoxData[self.box_index]["NewCharPosition"] == "Middle":
                brawlers_rewarded.pop(len(brawlers_rewarded) - 1)
                box_content["RewardCount"] = 2 + len(brawlers_rewarded)
                for i in range(len(brawlers_rewarded)):
                    box_content["Powerpoints" + str(i + 1)] = brawlers_rewarded[i]
            else:
                box_content["RewardCount"] = 2 + len(brawlers_rewarded)
                for i in range(len(brawlers_rewarded)):
                    box_content["Powerpoints" + str(i + 1)] = brawlers_rewarded[i]
            box_content["Brawler"] = choice(unlockable_brawlers)
            self.player.BrawlersUnlockedState[str(box_content["Brawler"])] = 1
            DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.BrawlersUnlockedState)

        elif reward[0] == "Nothing":
            box_content["RewardType"] = "OnlyPowerpoints"
            for i in range(len(brawlers_rewarded)):
                box_content["RewardCount"] += 1
                box_content["Powerpoints" + str(i + 1)] = brawlers_rewarded[i]
        else:
            box_content["RewardType"] = "Bonus"
            for i in range(len(brawlers_rewarded)):
                box_content["RewardCount"] += 1
                box_content["Powerpoints" + str(i + 1)] = brawlers_rewarded[i]
            box_content["RewardCount"] += 1
            box_content[reward[0]] = self.BoxData[self.box_index][reward[0]]

        # Box info
        self.writeVint(203) # CommandID
        self.writeVint(0)   # Unknown
        self.writeVint(1)   # Multipler
        self.writeVint(self.box_skin_id)  # BoxID
        # Box info end

        # Reward start
        self.writeVint(box_content["RewardCount"]) # Reward count

        if box_content["RewardType"] == "Brawler" and self.BoxData[self.box_index]["NewCharPosition"] == "Start":
            # Brawler start
            self.writeVint(1)                           # Reward amount
            self.writeScId(16, box_content["Brawler"])  # CsvID
            self.writeVint(1)                           # RewardID
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            # Brawler end

        else:
            DataBase.replaceValue(self, 'gold', self.player.gold + box_content["Gold"])
            # Gold start
            self.writeVint(box_content["Gold"]) # Reward amount
            self.writeVint(0) # SCID
            self.writeVint(7) # RewardID
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            # Gold end

            powerpoints_ammount = [randint(self.BoxData[self.box_index]["UpgradePoints"][0], self.BoxData[self.box_index]["UpgradePoints"][1]) for _ in range(len(brawlers_rewarded))]
            powerpoints_ammount.sort()
            for i in range(len(brawlers_rewarded)):
                self.player.brawlers_upgradium[str(brawlers_rewarded[i])] += powerpoints_ammount[i]
                DataBase.replaceValue(self, 'brawlersUpgradePoints', self.player.brawlers_upgradium)
                # Upgrade points start
                self.writeVint(powerpoints_ammount[i]) # Reward amount
                self.writeScId(16, box_content["Powerpoints" + str(i + 1)]) # BrawlerID
                self.writeVint(6) # RewardID
                self.writeVint(0)
                self.writeVint(0)
                self.writeVint(0)
                # Upgrade points end

            if box_content["RewardType"] == "Brawler":
                if self.BoxData[self.box_index]["NewCharPosition"] == "End" or self.BoxData[self.box_index]["NewCharPosition"] == "Middle":
                    # Brawler start
                    self.writeVint(1)  # Reward amount
                    self.writeScId(16, box_content["Brawler"])  # CsvID
                    self.writeVint(1)  # RewardID
                    self.writeVint(0)
                    self.writeVint(0)
                    self.writeVint(0)
                    # Brawler end

            if box_content["RewardType"] == "Bonus":
                for i in range(len(Boxes.reward_id)):
                    if Boxes.reward_id[i]["Name"] == reward[0]:
                        if reward[0] == "Gems":
                            ammountrewarded = choice(box_content[reward[0]])
                            self.player.gems = self.player.gems + ammountrewarded
                            DataBase.replaceValue(self, 'gems', self.player.gems)
                        elif reward[0] == "Tickets":
                            ammountrewarded = choice(box_content[reward[0]])
                            self.player.tickets = self.player.tickets + ammountrewarded
                            DataBase.replaceValue(self, 'tickets', self.player.tickets)
                        else:
                            ammountrewarded = choice(box_content[reward[0]])
                            self.player.tokensdoubler = self.player.tokensdoubler + ammountrewarded
                            DataBase.replaceValue(self, 'tokensdoubler', self.player.tokensdoubler)
                        self.writeVint(ammountrewarded) # Reward ammount
                        self.writeScId(0, Boxes.reward_id[i]['ID']) # RewardID
                        break

        # Box end
        for i in range(13):
            self.writeVint(0)