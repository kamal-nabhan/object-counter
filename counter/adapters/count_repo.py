from typing import List

from pymongo import MongoClient

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo
from counter.adapters.sqlalchemy_pg_adapter import ObjectCount_PG, engine


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(
                    key, stored_object_count.count + new_object_count.count
                )
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter["object_class"], counter["count"]))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one(
                {"object_class": value.object_class},
                {"$inc": {"count": value.count}},
                upsert=True,
            )


class CountPostgreSQLRepo(ObjectCountRepo):

    def __init__(self, db_url):
        self.engine, self.session = engine(db_url)

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        query = self.session.query(ObjectCount_PG)
        if object_classes:
            query = query.filter(ObjectCount_PG.object_class.in_(object_classes))
        return query.all()

    def update_values(self, new_values: List[ObjectCount]):
        for value in new_values:
            existing_count = (
                self.session.query(ObjectCount_PG)
                .filter_by(object_class=value.object_class)
                .first()
            )
            if existing_count:
                existing_count.count += value.count
            else:
                new_count = ObjectCount_PG(
                    object_class=value.object_class, count=value.count
                )
                self.session.add(new_count)
        self.session.commit()
