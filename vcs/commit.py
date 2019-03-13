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
        self._tree = None

    @property
    def sha(self):
        result = hashlib.sha1()
        result.update(self.author.encode())
        result.update(self.comment.encode())
        result.update(self._tree.sha.encode())
        return result.hexdigest()

    def set(self, tree):
        self._tree = tree
        # TODO: Добавить вычисление хэша коммита

    def get(self):
        return self._tree

    def apply(self, tree=None, current_tree=None):
        if current_tree is None:
            current_tree = self._tree
        if isinstance(tree, Transform):
            # Применить коммит к другому коммиту или трансформатору
            # TODO: Преобразование к трасформатору
            pass
        else:
            # Применить коммит к данным
            result = Tree(current_tree.name)
            for blob in current_tree.blobs:
                if tree is not None:
                    blob_before = next((blob_before for blob_before in tree.blobs if blob_before.name == blob.name),
                                       None)
                    if blob_before is None:
                        blob.apply()
                    else:
                        blob_before.apply()
                        blob.apply(blob_before)
                else:
                    blob.apply()
                result.blobs.append(blob)
                # result.blobs.append(Blob(blob.name, blob.sha, blob.size, changes=None, data=data))
            if current_tree.trees is not None:
                result.trees = list()
            for next_current_tree in current_tree.trees:
                if tree is not None:
                    tree_before = next((tree_before for tree_before in tree.trees
                                        if tree_before.name == next_current_tree.name), None)
                    result.trees.append(self.apply(tree_before, next_current_tree))
                else:
                    result.trees.append(self.apply(None, next_current_tree))
            return result

    def save(self):
        data = dict()
        data['parent'] = self.parent
        data['author'] = self.author
        data['comment'] = self.comment
        data['tree'] = self._tree.save()
        return json.dumps(data, sort_keys=True, indent=4)
