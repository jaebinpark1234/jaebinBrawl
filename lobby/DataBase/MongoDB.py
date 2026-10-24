import sys
import datetime
import json
import os
import copy
from Logic.Player import Player
from Utils.Helpers import Helpers

try:
    import pymongo
    from DataBase.MongoUtils import MongoUtils
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class LocalDB:
    def __init__(self, filepath="database.json"):
        self.filepath = filepath
        self.data = {"players": {}, "clubs": {}}
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[LocalDB] Save error: {e}")

    def create_player(self, doc):
        token = str(doc.get("Token"))
        self.data["players"][token] = copy.deepcopy(doc)
        self.save()

    def get_player_by_token(self, token):
        p = self.data["players"].get(str(token))
        return copy.deepcopy(p) if p else None

    def get_player_by_id(self, id):
        for p in self.data["players"].values():
            if p.get("ID") == id:
                return copy.deepcopy(p)
        return None

    def update_player(self, token, item, value):
        st = str(token)
        if st in self.data["players"]:
            self.data["players"][st][item] = copy.deepcopy(value)
            self.save()

    def update_all_players(self, query, item, value):
        for p in self.data["players"].values():
            match = all(p.get(k) == v for k, v in query.items())
            if match:
                p[item] = copy.deepcopy(value)
        self.save()

    def delete_player(self, token):
        st = str(token)
        if st in self.data["players"]:
            del self.data["players"][st]
            self.save()

    def delete_all_players(self, args):
        if not args:
            self.data["players"] = {}
        else:
            self.data["players"] = {
                k: v for k, v in self.data["players"].items()
                if not all(v.get(qk) == qv for qk, qv in args.items())
            }
        self.save()

    def load_all_players(self, args=None):
        if not args:
            return [copy.deepcopy(p) for p in self.data["players"].values()]
        res = []
        for p in self.data["players"].values():
            if all(p.get(k) == v for k, v in args.items()):
                res.append(copy.deepcopy(p))
        return res

    def load_all_players_sorted(self, args, element, element2=None):
        players = self.load_all_players(args)
        if element2 is not None:
            def sk(p):
                v = p.get(element, {})
                return v.get(element2, 0) if isinstance(v, dict) else 0
            players.sort(key=sk, reverse=True)
        else:
            players.sort(key=lambda p: p.get(element, 0), reverse=True)
        return players

    def create_club(self, id, doc):
        sid = str(id)
        self.data["clubs"][sid] = copy.deepcopy(doc)
        self.save()

    def load_club(self, id):
        sid = str(id)
        c = self.data["clubs"].get(sid)
        return copy.deepcopy(c) if c else None

    def update_club(self, id, item, value):
        sid = str(id)
        if sid in self.data["clubs"]:
            self.data["clubs"][sid][item] = copy.deepcopy(value)
            self.save()

    def load_all_clubs(self, args=None):
        if not args:
            return [copy.deepcopy(c) for c in self.data["clubs"].values()]
        res = []
        for c in self.data["clubs"].values():
            if all(c.get(k) == v for k, v in args.items()):
                res.append(copy.deepcopy(c))
        return res

    def load_all_clubs_sorted(self, args, element):
        clubs = self.load_all_clubs(args)
        clubs.sort(key=lambda c: c.get(element, 0), reverse=True)
        return clubs

    def delete_club(self, id):
        sid = str(id)
        if sid in self.data["clubs"]:
            del self.data["clubs"][sid]
            self.save()


class MongoDB:
    def __init__(self, conn_str):
        self.player = Player
        self.use_local = False

        if not PYMONGO_AVAILABLE or not conn_str:
            print(f"{Helpers.cyan}[INFO] Using local file database (database.json) for stability...")
            self.local_db = LocalDB("database.json")
            self.use_local = True
        else:
            try:
                print(f"{Helpers.cyan}[DEBUG] Connecting to Mongo DataBase...")
                self.client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=2000)
                self.client.server_info()
                self.database = self.client['Classic-Brawl']
                self.players = self.database['Players']
                self.clubs = self.database['Clubs']
                self.mongo_utils = MongoUtils()
            except Exception as e:
                print(f"{Helpers.yellow}[WARN] MongoDB connection failed ({e}). Falling back to local file database (database.json)...")
                self.local_db = LocalDB("database.json")
                self.use_local = True

        self.data = {
            'Name': 'Guest',
            'NameSet': False,
            'Gems': Player.gems,
            'Trophies': Player.trophies,
            'Tickets': Player.tickets,
            'Resources': Player.resources,
            'TokenDoubler': 0,
            'HighestTrophies': Player.high_trophies,
            'HomeBrawler': 0,
            'TrophyRoadReward': 1,
            'ExperiencePoints': Player.exp_points,
            'ProfileIcon': 0,
            'NameColor': 0,
            'UnlockedBrawlers': Player.brawlers_unlocked,
            'BrawlersTrophies': Player.brawlers_trophies,
            'BrawlersHighestTrophies': Player.brawlers_high_trophies,
            'BrawlersLevel': Player.brawlers_level,
            'BrawlersPowerPoints': Player.brawlers_powerpoints,
            'UnlockedSkins': Player.unlocked_skins,
            'SelectedSkins': Player.selected_skins,
            'SelectedBrawler': 0,
            'Region': Player.region,
            'SupportedContentCreator': "재빈브롤",
            'StarPower': Player.starpower,
            'Gadget': Player.gadget,
            'BrawlPassActivated': False,
            'WelcomeMessageViewed': False,
            'ClubID': 0,
            'ClubRole': 1,
            'TimeStamp': str(datetime.datetime.now())
        }

        self.club_data = {
            'Name': '',
            'Description': '',
            'Region': '',
            'BadgeID': 0,
            'Type': 0,
            'Trophies': 0,
            'RequiredTrophies': 0,
            'FamilyFriendly': 0,
            'Members': [],
            'Messages': []
        }

    def merge(self, dict1, dict2):
        return (dict1.update(dict2))

    def create_player_account(self, id, token):
        auth = {
            'ID': id,
            'Token': token,
        }
        auth.update(self.data)
        if self.use_local:
            self.local_db.create_player(auth)
        else:
            self.mongo_utils.insert_data(self.players, auth)

    def load_player_account(self, id, token):
        if self.use_local:
            result = self.local_db.get_player_by_token(token)
            if result:
                for x in self.data:
                    if x not in result:
                        self.update_player_account(token, x, self.data[x])
                result = self.local_db.get_player_by_token(token)
            return result
        else:
            query = {"Token": token}
            result = self.mongo_utils.load_document(self.players, query)
            if result:
                for x in self.data:
                    if x not in result:
                        self.update_player_account(token, x, self.data[x])
                query = {"Token": token}
                result = self.mongo_utils.load_document(self.players, query)
            return result

    def load_player_account_by_id(self, id):
        if self.use_local:
            return self.local_db.get_player_by_id(id)
        else:
            query = {"ID": id}
            return self.mongo_utils.load_document(self.players, query)

    def update_player_account(self, token, item, value):
        if self.use_local:
            self.local_db.update_player(token, item, value)
        else:
            query = {"Token": token}
            self.mongo_utils.update_document(self.players, query, item, value)

    def update_all_players(self, query, item, value):
        if self.use_local:
            self.local_db.update_all_players(query, item, value)
        else:
            self.mongo_utils.update_all_documents(self.players, query, item, value)

    def delete_all_players(self, args):
        if self.use_local:
            self.local_db.delete_all_players(args)
        else:
            self.mongo_utils.delete_all_documents(self.players, args)

    def delete_player(self, token):
        if self.use_local:
            self.local_db.delete_player(token)
        else:
            query = {"Token": token}
            self.mongo_utils.delete_document(self.players, query)

    def load_all_players(self, args):
        if self.use_local:
            return self.local_db.load_all_players(args)
        else:
            return self.mongo_utils.load_all_documents(self.players, args)

    def load_all_players_sorted(self, args, element, element2: str = None):
        if self.use_local:
            return self.local_db.load_all_players_sorted(args, element, element2)
        else:
            return self.mongo_utils.load_all_documents_sorted(self.players, args, element, element2)

    def create_club(self, id, data):
        auth = {'ID': id}
        auth.update(data)
        if self.use_local:
            self.local_db.create_club(id, auth)
        else:
            self.mongo_utils.insert_data(self.clubs, auth)

    def update_club(self, id, item, value):
        if self.use_local:
            self.local_db.update_club(id, item, value)
        else:
            query = {"ID": id}
            self.mongo_utils.update_document(self.clubs, query, item, value)

    def load_club(self, id):
        if self.use_local:
            result = self.local_db.load_club(id)
            if result:
                for x in self.club_data:
                    if x not in result:
                        self.update_club(id, x, self.club_data[x])
                result = self.local_db.load_club(id)
            return result
        else:
            query = {"ID": id}
            result = self.mongo_utils.load_document(self.clubs, query)
            if result:
                for x in self.club_data:
                    if x not in result:
                        self.update_club(id, x, self.club_data[x])
                query = {"ID": id}
                result = self.mongo_utils.load_document(self.clubs, query)
            return result

    def load_all_clubs_sorted(self, args, element):
        if self.use_local:
            return self.local_db.load_all_clubs_sorted(args, element)
        else:
            return self.mongo_utils.load_all_documents_sorted(self.clubs, args, element, None)

    def load_all_clubs(self, args):
        if self.use_local:
            return self.local_db.load_all_clubs(args)
        else:
            return self.mongo_utils.load_all_documents(self.clubs, args)

    def delete_club(self, id):
        if self.use_local:
            self.local_db.delete_club(id)
        else:
            query = {"ID": id}
            self.mongo_utils.delete_document(self.clubs, query)
