import hashlib
import json

from vcs.blob import Blob
from vcs.transform import Transform
from vcs.tree import Tree


class Commit(Transform):
    def __init__(self, parent, author, comment):
        self.parent = parent
        self.author = author
        self.comment = comment
        self.childrens = list()
        self._tree = None

    @property
    def sha(self):
        result = hashlib.sha1()
        result.update(self.author.encode())
        result.update(self.comment.encode())
        result.update(self._tree.sha.digest())
        return result

    def set(self, tree):
        self._tree = tree
        # ToDo: Добавить вычисление хэша коммита

    def get(self):
        return self._tree

    @property
    def is_last(self):
        return len(self.childrens) == 0

    def apply(self, tree=None, commit_tree=None):
        if commit_tree is None:
            commit_tree = self._tree
        if isinstance(tree, Transform):
            # Применить коммит к другому коммиту или трансформатору
            # ToDo: Преобразование к трасформатору
            pass
        else:
            # Применить коммит к данным
            result = Tree(commit_tree.name)
            for blob in commit_tree.blobs:
                if tree is not None:
                    blob_before = next((blob_before for blob_before in tree.blobs if blob_before.name == blob.name),
                                       None)
                    if blob_before is None:
                        # blob.clear() ?
                        data = blob.data()
                    else:
                        # blob.clear() ?
                        data = blob.data(blob_before.data())
                else:
                    data = blob.data()
                result.blobs.append(Blob(blob.name, blob.sha, blob.size, None, data))
            for next_commit_tree in commit_tree.trees:
                if tree is not None:
                    tree_before = next((tree_before for tree_before in tree.blobs
                                        if tree_before.name == next_commit_tree.name), None)
                    result.blobs.append(self.apply(tree_before, next_commit_tree))
                else:
                    result.blobs.append(self.apply(None, next_commit_tree))
            return result

    def roll_back(self, tree, commit_tree=None):
        if commit_tree is None:
            commit_tree = self._tree
        if isinstance(tree, Transform):
            # Применить коммит к другому коммиту или трансформатору
            pass
        else:
            # Применить коммит к данным
            result = Tree(commit_tree.name)
            for blob in commit_tree.blobs:
                if tree is not None:
                    blob_after = next((blob_after for blob_after in tree.blobs if blob_after.name == blob.name),
                                      None)
                    if blob_after is None:
                        # blob.clear() ?
                        tree = blob.reset()
                    else:
                        # blob.clear() ?
                        tree = blob.reset(blob_after.data())
                else:
                    tree = blob.reset()
                result.blobs.append(Blob(blob.name, blob.sha, blob.size, None, tree))
            for next_commit_tree in commit_tree.trees:
                if tree is not None:
                    tree_after = next((tree_before for tree_before in tree.blobs
                                       if tree_before.name == next_commit_tree.name), None)
                    result.blobs.append(self.roll_back(tree_after, next_commit_tree))
                else:
                    result.blobs.append(self.roll_back(None, next_commit_tree))
            return result

    def json_info(self):
        data = dict()
        data['parent'] = self.parent
        data['author'] = self.author
        data['comment'] = self.comment
        data['sha'] = self.sha
        data['childrens'] = list()
        for child in self.childrens:
            data['childrens'].append(child.sha)
        return json.dump(data, sort_keys=True)
