import pymongo
from daemon.src.Params import Params


class DB(object):
    def __init__(self):
        client = pymongo.MongoClient('mongodb://%s:%s@127.0.0.1' % (Params.mongo_user, Params.mongo_pass))
        self.db = client.royale_database

        if 'clanWar' not in self.db.battles_collection.index_information():
            self.db.battles_collection.create_index('clanWar')
            self.db.battles_collection.create_index([('utcTime', pymongo.DESCENDING)])

    def getPreviusWar(self):
        return self.db.clan_war.find_one(sort=[("createdDate", -1)])
