import pymongo
from telegram.src.Params import Params


class DB(object):
    def __init__(self):
        client = pymongo.MongoClient('mongodb://%s:%s@127.0.0.1' % (Params.mongo_user, Params.mongo_pass))
        self.db = client.royale_database

        if 'clanWar' not in self.db.battles_collection.index_information():
            self.db.battles_collection.create_index('clanWar')
            self.db.battles_collection.create_index([('utcTime', pymongo.DESCENDING)])

    def addBattle(self, battle):
        self.db.battles_collection.insert_one(battle)

    def battleIsSaved(self, battle):
        query = {
            "utcTime": battle['utcTime'],
            "player.tag": battle['player']['tag']
        }

        return self.db.battles_collection.find_one(query) is not None

    def addBattleOfClan(self, battle):
        self.db.clan_war_collection.insert_one(battle)

    def addClanWar(self, clan_war):
        self.db.clan_war.insert_one(clan_war)

    def clanWarIsSaved(self, battle):
        query = {
            "createdDate": battle['createdDate']
        }

        return self.db.clan_war.find_one(query) is not None

    def removeOldClanWar(self):
        # Obtener fecha actual y restar un mes
        self.db.clan_war.remove('{ access_time : {"$lt" : new Date('+year+','+month+','+day+') } }')
