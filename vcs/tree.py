import json
import hashlib


class Tree:
    """
    Объект представления директории, находящейся в репозитории
    """
    def __init__(self, name):
        self.name = name
        self.blobs = list()
        self.trees = list()

    @property
    def sha(self):
        result = hashlib.sha1()
        for blob in self.blobs:
            result.update(blob.sha.digest())
        for tree in self.trees:
            result.update(tree.sha)
        return result

    def json(self):
        data = dict()
        data['name'] = self.name
        data['blobs'] = list()
        for blob in self.blobs:
            data['blobs'].append(blob.save())
        data['trees'] = [tree.sha for tree in self.trees]
        return json.dump(data, sort_keys=True, ident=4)
