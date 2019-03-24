import hashlib

from vcs.blob import Blob
from vcs.changes import Changes
from vcs.exceptions import DataError


class Tree:
    """
    Объект представления директории, находящейся в репозитории
    """

    def __init__(self, name=None):
        self.name = name
        self.blobs = list()
        self.trees = list()

    @property
    def sha(self):
        result = hashlib.sha1()
        for blob in self.blobs:
            result.update(blob.sha.encode())
        for tree in self.trees:
            result.update(tree.sha.encode())
        return result.hexdigest()

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

    def load(self, data):
        if 'name' not in data:
            return None
        self.name = data['name']
        if 'blobs' in data:
            for blob in data['blobs']:
                try:
                    changes = Changes()
                    changes.load(blob['changes'])
                    self.blobs.append(Blob(blob['name'],
                                           blob['sha'],
                                           blob['size'],
                                           changes))
                except KeyError as e:
                    raise DataError('Key ' + str(e) + ' not found')
        if 'trees' in data:
            for t in data['trees']:
                tree = Tree()
                tree.load(t)
                self.trees.append(tree)
