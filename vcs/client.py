import hashlib
import os
from functools import reduce

from vcs.blob import Blob
from vcs.commit import Commit
from vcs.diff import Diff
from vcs.tree import Tree
from vcs.repository import Repository
from vcs.exceptions import *


class Client:
    @staticmethod
    def init(directory=os.getcwd()):
        Repository.init(directory=directory)

    @staticmethod
    def add(file, directory=os.getcwd()):
        Repository.add_indexing(file, directory=directory)

    @staticmethod
    def get(branch, commit_sha, directory=os.getcwd()):
        commit = Repository.load_commit(branch, commit_sha, directory=directory)
        # if commit is None:
        #     return None
        commits = list()
        while commit.parent is not None:
            commits.append(commit)
            if Repository.get_parent_branch(branch, directory=directory) is not None and\
                    Repository.get_parent_branch(branch, directory=directory)[1] == commit.parent:
                branch, commit = Repository.get_parent_branch(branch, directory=directory)
                commit = Repository.load_commit(branch, commit, directory=directory)
            else:
                commit = Repository.load_commit(branch, commit.parent, directory=directory)

        commits.append(commit)
        if len(commits) == 0:
            return None
        commits.reverse()
        commits[0] = commits[0].apply()
        return reduce(lambda a, x: x.apply(a), commits)

    @staticmethod
    def commit(author, comment, tag=None, directory=os.getcwd()):
        branch = Repository.get_current_branch(directory=directory)
        indexing_files = Repository.get_indexing(directory=directory)
        tree = Tree('.')
        for file in indexing_files:
            path = os.path.relpath(os.path.abspath(os.path.join(directory, file)), directory)
            if os.path.exists(os.path.join(directory, path)):
                *path_list, file = path.split(os.sep)
                if Repository.get_head_commit(branch, directory=directory) is not None:
                    last_tree = Client.get(branch, Repository.get_current_commit(branch, directory=directory), directory)
                elif Repository.get_parent_branch(branch, directory=directory) is not None:
                    last_tree = Client.get(Repository.get_parent_branch(branch, directory=directory)[0],
                                           Repository.get_parent_branch(branch, directory=directory)[1], directory)
                else:
                    last_tree = None
                prev_tree = tree
                for sub_path in path_list:
                    next_tree = Tree(sub_path)
                    prev_tree.trees.append(next_tree)
                    prev_tree = next_tree
                    if last_tree is not None:
                        last_tree = [tree for tree in last_tree.trees if tree.name == sub_path]
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
                prev_tree.blobs.append(Blob(file, hashlib.sha1(data.encode()).hexdigest(), len(data),
                                       Diff.diff(None if last_data is None else last_data.data, data)))
        parent_commit = Repository.get_current_commit(branch, directory=directory)
        if parent_commit is None and Repository.get_parent_branch(branch, directory=directory) is not None:
            parent_commit = Repository.get_parent_branch(branch, directory=directory)[1]
        commit = Commit(parent_commit, author, comment, tag)
        commit.set(tree)
        Repository.save_commit(branch, commit, directory=directory)
        Repository.set_current_commit(branch, commit.sha, directory=directory)
        if Repository.get_head_commit(branch, directory=directory) is None:
            Repository.set_head_commit(branch, commit.sha, directory=directory)
        Repository.clear_indexing(directory=directory)
        return commit.sha

    @staticmethod
    def reset(commit_sha, directory=os.getcwd()):
        tree = Client.get(Repository.get_current_branch(directory=directory), commit_sha, directory)
        current_tree = Client.get(Repository.get_current_branch(directory=directory),
                                  Repository.get_current_commit(Repository.get_current_branch(directory=directory),
                                                                directory=directory),
                                  directory=directory)
        Repository.remove(current_tree, directory)
        Repository.write(tree, directory)

    @staticmethod
    def log(directory=os.getcwd()):
        log_commits = list()
        branch = Repository.get_current_branch(directory=directory)
        commit = Repository.load_commit(branch, Repository.get_current_commit(branch))
        while commit is not None:
            log_commits.append((commit.sha, commit.author, commit.comment, commit.tag))
            commit = None if commit.parent is None else Repository.load_commit(commit.parent, directory)
        return reversed(log_commits)

    @staticmethod
    def branch(name, directory=os.getcwd()):
        current_branch = Repository.get_current_branch(directory=directory)
        Repository.add_branch(name, directory=directory)
        Repository.set_parent_branch(name, current_branch,
                                     Repository.get_current_commit(current_branch, directory=directory),
                                     directory=directory)

    @staticmethod
    def checkout(branch, directory=os.getcwd()):
        # TODO: Проверить, есть ли не зафиксированные изменения
        commit = Repository.get_current_commit(branch, directory=directory)
        Repository.clear(directory=directory)
        if commit is not None:
            Repository.write(Client.get(branch, commit, directory=directory), directory=directory)
        else:
            parent = Repository.get_parent_branch(branch, directory=directory)
            if parent[1] is not None:
                Repository.write(Client.get(parent[0], parent[1], directory=directory),
                                 directory=directory)
        Repository.set_current_branch(branch, directory=directory)
