from mb_base1.db import BaseDB
from mb_std.mongo import MongoCollection
from pymongo.database import Database

from app.models import Group, Proxy


class DB(BaseDB):
    def __init__(self, database: Database):
        super().__init__(database)
        self.group: MongoCollection[Group] = Group.init_collection(database)
        self.proxy: MongoCollection[Proxy] = Proxy.init_collection(database)
