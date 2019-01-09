import hashlib
import os
import json

from vcs.blob import Blob
from vcs.changes import Changes
from vcs.commit import Commit
from vcs.diff import Diff
from vcs.tree import Tree


class LocalInterface:
    @staticmethod
    def vcs_path():
        return '.vcs'

    @staticmethod
    def check_repo():
        return os.path.exists('.vcs')

    @staticmethod
    def init(directory=os.getcwd()):
        if os.path.exists(directory):
            work_path = os.path.join(directory, '.vcs')
            if not os.path.exists(work_path):
                os.makedirs(work_path)
            if not os.path.exists(os.path.join(work_path, 'INDEXING')):
                open(os.path.join(work_path, 'INDEXING'), 'tw').close()
        else:
            if os.path.isfile(directory):
                raise ValueError("It is file: " + directory)

    @staticmethod
    def add(file):
        # LocalInterface.check_repo()
        if os.path.exists(os.path.join(os.getcwd(), file)):
            path = os.path.relpath(os.path.abspath(os.path.join(os.getcwd(), file)), os.getcwd())
            with open(os.path.join(LocalInterface.vcs_path(), 'INDEXING'), 'r+') as f:
                try:
                    indexing_files = json.load(f)
                except ValueError:
                    indexing_files = {}
                f.seek(0)
                f.truncate(0)
                if 'files' not in indexing_files:
                    indexing_files['files'] = list()
                indexing_files['files'].append(path)
                indexing_files['files'] = list(set(indexing_files['files']))
                json.dump(indexing_files, f, sort_keys=True, indent=4)

    @staticmethod
    def commit(author, comment):
        with open(os.path.join(LocalInterface.vcs_path(), 'INDEXING'), 'r') as f:
            try:
                indexing_files = json.load(f)
            except ValueError:
                return
            if 'files' not in indexing_files:
                return
            else:
                indexing_files = indexing_files['files']
            tree = Tree('.')
            for file in indexing_files:
                path = os.path.relpath(os.path.abspath(os.path.join(os.getcwd(), file)), os.getcwd())
                if os.path.exists(path):
                    *path_list, file = path.split(os.sep)
                    for path in path_list:
                        next_tree = Tree(path)
                        tree.trees.append(next_tree)
                        tree = next_tree
                    fd = open(path, 'r')
                    data = fd.read()
                    tree.blobs.append(Blob(file, hashlib.sha1(data.encode()), 0, None, data))
            commit = Commit(None, author, comment)
            # commit.set(tree)
            LocalInterface.save_commit(commit)

    @staticmethod
    def reset(commit_sha):
        pass

    @staticmethod
    def checkout(sha):
        pass

    @staticmethod
    def save_tree(path, tree):
        with open(os.path.join(path, tree.sha.hexdigest()), 'w') as f:
            f.write(tree.json())
        for t in tree.trees:
            LocalInterface.save_tree(path, t)

    @staticmethod
    def load_tree(path, root):
        with open(os.path.join(path, root), 'r') as f:
            t = json.load(f.read())
        tree = Tree(t['name'])
        for blob in t['blobs']:
            Blob(blob['name'], blob['sha'], blob['size'], Changes.load(blob['changes']))
        for tree_sha in t['trees']:
            tree.trees.append(LocalInterface.load_tree(path, tree_sha))
        return tree

    @staticmethod
    def save_commit(commit):
        # Проверить целостность файлов
        print(LocalInterface.vcs_path(), 'commits', commit.sha.hexdigest())
        if os.path.exists(os.path.join(LocalInterface.vcs_path(), 'commits', commit.sha.hexdigest())):
            raise ValueError('Commit exist')
        work_path = os.path.join(LocalInterface.vcs_path(), 'commits', commit.sha.hexdigest())
        os.makedirs(work_path)
        with open(os.path.join(work_path, 'info'), 'w') as f:
            f.write(commit.json_info())
        LocalInterface.save_tree(work_path, commit.get())

    @staticmethod
    def load_commit(commit_sha):
        if not os.path.exists(os.path.join(LocalInterface.vcs_path(), 'commits', commit_sha.hexdigest())):
            raise ValueError('Commit not found')
        work_path = os.path.join(LocalInterface.vcs_path(), 'commits', commit_sha.hexdigest())
        with open(os.path.join(work_path, 'info'), 'r') as f:
            info = json.load(f.read())
        commit = Commit(info['parent'], info['author'], info['comment'])
        commit.set(LocalInterface.load_tree(os.path.join(LocalInterface.vcs_path(), 'commits', commit_sha),
                                            info['root']))
        return commit
