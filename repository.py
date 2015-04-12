class MongoRepository():
    def __init__(self, db):
        self.db = db

    def save(self, rangevote):
        rangevotes = self.db[type(rangevote).__name__.lower()]
        rangevotes.insert(rangevote.serialize())

    def get(self, id):
        rangevotes = self.db['rangevote']
        element = rangevotes.find_one({"id": str(id)})
        del element['_id']
        return element


class MockRepository():
    def __init__(self):
        self.saved_called = False
        self.get_called = False

    def save(self, aggregate):
        self.saved_called = True

    def get(self, id):
        self.get_called = True
