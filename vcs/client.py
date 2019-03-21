import hashlib
import os
import json
from functools import reduce

from vcs.blob import Blob
# from vcs.changes import Changes
from vcs.commit import Commit
from vcs.diff import Diff
from vcs.tree import Tree
from vcs.exceptions import *


class Client:
    @staticmethod
    def vcs_path():
        return '.vcs'

    @staticmethod
    def check_repo():
        return os.path.exists('.vcs')

    @staticmethod
    def init(directory=os.getcwd()):
        try:
            if not os.path.exists(directory):
                raise InitError('Repository directory does not exist.')
            if not os.path.isdir(directory):
                raise InitError('Path ' + directory + ' is not a dir.')
            work_path = os.path.relpath(os.path.abspath(os.path.join(directory, Client.vcs_path())))
            if os.path.exists(work_path):
                raise InitError('Repository already exist.')
            os.makedirs(work_path)
            open(os.path.join(work_path, 'INDEXING'), 'tw').close()
            open(os.path.join(work_path, 'HEAD'), 'tw').close()
            open(os.path.join(work_path, 'CURRENT'), 'tw').close()
            os.makedirs(os.path.join(work_path, 'commits'))
        except OSError as e:
            raise InitError(str(e))

    @staticmethod
    def add(file, directory=os.getcwd()):
        Client.check_repo()
        if not os.path.exists(os.path.join(directory, file)):
            raise AddError('File ' + file + ' does not exist.')
        path = os.path.relpath(os.path.abspath(os.path.join(directory, file)), directory)
        with open(os.path.join(directory, Client.vcs_path(), 'INDEXING'), 'r+') as f:
            # if e:
            #     raise AddError('Repository structure broken. INDEXING file not found.')
            try:
                indexing_files = json.load(f)
            except ValueError:
                indexing_files = {}
            f.seek(0)
            f.truncate(0)
            if 'files' not in indexing_files:
                indexing_files['files'] = list()
            # TODO: Добавлять только относительный путь
            indexing_files['files'].append(path)
            indexing_files['files'] = list(set(indexing_files['files']))
            json.dump(indexing_files, f, sort_keys=True, indent=4)

    @staticmethod
    def get(commit_sha, directory=os.getcwd()):
        commit = Client.load_commit(commit_sha, directory)
        # if commit is None:
        #     return None
        commits = list()
        while commit.parent is not None:
            commits.append(commit)
            commit = Client.load_commit(commit.parent, directory)
        commits.append(commit)
        if len(commits) == 0:
            return None
        commits.reverse()
        commits[0] = commits[0].apply()
        return reduce(lambda a, x: x.apply(a), commits)

    @staticmethod
    def commit(author, comment, tag=None, directory=os.getcwd()):
        with open(os.path.join(directory, Client.vcs_path(), 'INDEXING'), 'r') as f:
            # if e:
            #     raise AddError('Repository structure broken. INDEXING file not found.')
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
                path = os.path.relpath(os.path.abspath(os.path.join(directory, file)), directory)
                if os.path.exists(os.path.join(directory, path)):
                    *path_list, file = path.split(os.sep)
                    if Client.get_head_sha(directory) is not None:
                        last_tree = Client.get(Client.get_current_sha(directory), directory)
                    else:
                        last_tree = None
                    for path in path_list:
                        next_tree = Tree(path)
                        tree.trees.append(next_tree)
                        tree = next_tree
                        if last_tree is not None:
                            last_tree = [tree for tree in last_tree.trees if tree.name == path]
                            if len(last_tree) > 0:
                                last_tree = last_tree[0]
                            else:
                                last_tree = None

                    fd = open(os.path.join(directory, path), 'r')
                    data = fd.read()
                    fd.close()

                    last_data = None
                    if last_tree is not None:
                        last_data = [blob for blob in last_tree.blobs if blob.name == file]
                        if len(last_data) > 0:
                            last_data = last_data[0]

                    tree.blobs.append(Blob(file, hashlib.sha1(data.encode()).hexdigest(), len(data),
                                           Diff.diff(None if last_data is None else last_data.data, data)))
            commit = Commit(Client.get_current_sha(directory), author, comment, tag)
            commit.set(tree)
            Client.save_commit(commit, directory)
            Client.set_current_sha(commit.sha, directory)
            if Client.get_head_sha(directory) is None:
                Client.set_head_sha(commit.sha, directory)
            with open(os.path.join(directory, Client.vcs_path(), 'INDEXING'), 'r+') as f:
                f.truncate(0)
        return commit.sha

    @staticmethod
    def reset(commit_sha, directory=os.getcwd()):
        tree = Client.get(commit_sha, directory)
        current_tree = Client.get(Client.get_current_sha(directory), directory)
        Client.remove(current_tree, directory)
        Client.write(tree, directory)

    @staticmethod
    def log(directory=os.getcwd()):
        log_commits = list()
        commit = Client.load_commit(Client.get_current_sha(directory), directory)
        while commit is not None:
            log_commits.append((commit.sha, commit.author, commit.comment, commit.tag))
            commit = None if commit.parent is None else Client.load_commit(commit.parent, directory)
        return reversed(log_commits)

    @staticmethod
    def remove(tree, directory=os.getcwd()):
        for blob in tree.blobs:
            path = os.path.join(directory, tree.name, blob.name)
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError as e:
                    raise DataError(str(e))
        for t in tree.trees:
            Client.remove(t, os.path.join(directory, tree.name))
            path_dir = os.path.join(directory, tree.name, t.name)
            if os.path.exists(path_dir) and os.path.isdir(path_dir) and len(os.listdir(path_dir)) == 0:
                os.rmdir(path_dir)

    @staticmethod
    def write(tree, directory=os.getcwd()):
        for blob in tree.blobs:
            path = os.path.join(directory, tree.name, blob.name)
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError as e:
                    raise DataError(str(e))
            fd = open(path, 'w')
            fd.write(blob.data)
            fd.close()
        for t in tree.trees:
            path_dir = os.path.join(directory, tree.name, t.name)
            if os.path.exists(path_dir):
                if os.path.isfile(path_dir):
                    os.remove(path_dir)
                    os.mkdir(path_dir)
            else:
                os.mkdir(path_dir)
            Client.write(t, os.path.join(directory, tree.name))

    @staticmethod
    def checkout(sha):
        pass

    @staticmethod
    def get_current_sha(directory=os.getcwd()):
        with open(os.path.join(directory, Client.vcs_path(), 'CURRENT'), 'r') as f:
            # if e:
            #     raise RepoError('Repository structure broken. CURRENT file not found.')
            sha = f.read()
            return None if sha == '' else sha

    @staticmethod
    def set_current_sha(sha, directory=os.getcwd()):
        with open(os.path.join(directory, Client.vcs_path(), 'CURRENT'), 'w') as f:
            # if e:
            #     raise RepoError('Repository structure broken. CURRENT file not found.')
            f.seek(0)
            f.write(sha)
            f.truncate()

    @staticmethod
    def get_head_sha(directory=os.getcwd()):
        with open(os.path.join(directory, Client.vcs_path(), 'HEAD'), 'r') as f:
            # if e:
            #     raise RepoError('Repository structure broken. HEAD file not found.')
            sha = f.read()
            return None if sha == '' else sha

    @staticmethod
    def set_head_sha(sha, directory=os.getcwd()):
        with open(os.path.join(directory, Client.vcs_path(), 'HEAD'), 'w') as f:
            # if e:
            #     raise RepoError('Repository structure broken. CURRENT file not found.')
            f.seek(0)
            f.write(sha)
            f.truncate()

    @staticmethod
    def save_commit(commit, directory=os.getcwd()):
        work_path = os.path.join(directory, Client.vcs_path(), 'commits', commit.sha)
        if os.path.exists(work_path):
            raise DataError('Commit ' + commit.sha + ' exist')
        with open(work_path, 'w') as f:
            # if e:
            #     raise DataError('File ' + work_path + ' creating error.')
            try:
                f.write(commit.save())
            except IOError as e:
                raise RepoError(e)

    @staticmethod
    def load_commit(commit_sha, directory=os.getcwd()):
        work_path = os.path.join(directory, Client.vcs_path(), 'commits', '' if commit_sha is None else commit_sha)
        if not os.path.exists(work_path):
            raise DataError('Commit not found.')
        if not os.path.isfile(work_path):
            raise InitError('Path ' + work_path + ' is not a file.')
        with open(work_path, 'r') as f:
            # if e:
            #     raise DataError('File ' + work_path + ' not found.')
            try:
                commit_json = json.load(f)
            except ValueError:
                return None
            try:
                commit = Commit(commit_json['parent'], commit_json['author'], commit_json['comment'],
                                commit_json.get('tag'))
                tree = Tree()
                tree.load(commit_json['tree'])
                commit.set(tree)
            except KeyError as e:
                raise DataError('Key ' + str(e) + ' not found')
        return commit
