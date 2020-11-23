import pymongo
from pymongo import MongoClient


class SMongoFilter:

    def and_filter(self, *args):
        res = []
        for filter in args:
            res.append(filter)
        return {"$and": res}

    def or_filter(self, *args):
        res = []
        for filter in args:
            res.append(filter)
        return {"$or": res}

    def between(self, name: str, value1: int, value2: int):
        return self.and_filter(self.bigger_include(name, value1), self.smaller_include(name, value2))

    def bigger_include(self, name: str, value):
        return {name: {"$gte": value}}

    def bigger(self, name: str, value):
        return {name: {"$gt": value}}

    def smaller_include(self, name: str, value):
        return {name: {"$lte": value}}

    def smaller(self, name: str, value):
        return {name: {"$lt": value}}

    def data_is(self, name: str, data):
        return {name: data}

    def data_is_not(self, data):
        return {"$not": data}


class SMongoDB:

    def __init__(self, ip: str, port: int, user: str, password: str, db: str):
        self.filter = SMongoFilter()
        self.ip = ip
        self.port = port

        self.user = user
        self.password = password

        self.mongo = MongoClient(ip, port)
        self.db = self.mongo[db]
        self.db.authenticate(user, password)

    def set_db(self, database):
        self.db = self.mongo[database]
        self.db.authenticate(self.user, self.password)

    def insert_data(self, collection: str, data):
        if type(data) != dict and type(data) != list:
            return None
        if type(data) == dict:
            return self.db[collection].insert_one(data).inserted_id
        return self.db[collection].insert_many(data).inserted_ids

    def create_sort_object(self, name: str, direction: str):
        # ASC DESC
        if direction == "ASC":
            direction = pymongo.ASCENDING
        else:
            direction = pymongo.DESCENDING
        return (name, direction)

    def find(self, collection: str, filter_dict: dict, limit: int, column: list, sort: tuple = None, find_one=False):

        column_dict = {}
        for column in column:
            column_dict[column] = 1

        if find_one:
            return self.db[collection].find_one(filter_dict, column_dict)

        if limit == 0:
            res = self.db[collection].find(filter_dict, column_dict)
        else:
            res = self.db[collection].find(filter_dict, column_dict).limit(limit)

        if res is None:
            return None
        if sort is not None:
            res = res.sort(sort[0], sort[1])
        output = []
        for record in res:
            output.append(record)
        res.close()
        return output

    def find_ids(self, collection: str, filter_dict: dict, limit: int, sort: tuple = None, find_one=False):
        res = self.find(collection, filter_dict, limit, ["_id"], sort, find_one)
        if res is None:
            return []
        out = []
        for x in res:
            out.append(x["_id"])
        return out

    def delete(self, collection: str, filter_dict: dict):
        result = self.db[collection].delete_many(filter_dict).raw_result
        return result

    def update(self, collection: str, filter_dict: dict, update_content: dict):
        result = self.db[collection].update_many(filter_dict, {"$set": update_content})
        return result

    def does_collection_exist(self, collection: str):
        return collection in self.db.list_collection_names()