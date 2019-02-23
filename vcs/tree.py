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

    def save(self):
        data = dict()
        data['name'] = self.name
        data['blobs'] = list()
        for blob in self.blobs:
            data['blobs'].append(blob.save())
        data['trees'] = list()
        for tree in self.trees:
            data['trees'].append(tree.save())
        return data
