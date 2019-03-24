import json
import os
import shutil

from vcs.commit import Commit
from vcs.exceptions import *
from vcs.tree import Tree


class Repository:
    @staticmethod
    def vcs_path(directory=os.getcwd()):
        return os.path.abspath(os.path.join(directory, '.vcs'))

    @staticmethod
    def check_repo(directory=os.getcwd()):
        return os.path.exists(Repository.vcs_path(directory))

    @staticmethod
    def init(directory=os.getcwd()):
        try:
            if not os.path.exists(directory):
                raise InitError('Repository directory does not exist.')
            if not os.path.isdir(directory):
                raise InitError('Path ' + directory + ' is not a dir.')
            work_path = Repository.vcs_path(directory)
            if os.path.exists(work_path):
                raise InitError('Repository already exist.')
            os.makedirs(work_path)
            open(os.path.join(work_path, 'INDEXING'), 'tw').close()
            open(os.path.join(work_path, 'BRANCH'), 'tw').close()
            os.makedirs(os.path.join(work_path, 'commits'))
            Repository.add_branch('master', directory)
            Repository.set_current_branch('master', directory)
        except OSError as e:
            raise InitError(str(e))

    @staticmethod
    def add_indexing(file, directory=os.getcwd()):
        Repository.check_repo()
        if not os.path.exists(os.path.join(directory, file)):
            raise AddError('File ' + file + ' does not exist.')
        path = os.path.relpath(os.path.abspath(os.path.join(directory, file)), directory)
        with open(os.path.join(Repository.vcs_path(directory), 'INDEXING'), 'r+') as f:
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
    def get_indexing(directory=os.getcwd()):
        Repository.check_repo()
        with open(os.path.join(Repository.vcs_path(directory), 'INDEXING'), 'r+') as f:
            try:
                indexing_files = json.load(f)
            except ValueError:
                indexing_files = {}
            return indexing_files['files']

    @staticmethod
    def clear_indexing(directory=os.getcwd()):
        Repository.check_repo()
        with open(os.path.join(Repository.vcs_path(directory), 'INDEXING'), 'r+') as f:
            f.truncate(0)

    @staticmethod
    def get_current_branch(directory=os.getcwd()):
        with open(os.path.join(Repository.vcs_path(directory), 'BRANCH'), 'r') as f:
            return f.read()

    @staticmethod
    def set_current_branch(branch, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'BRANCH'), 'w') as f:
            f.seek(0)
            f.write(branch)
            f.truncate()

    @staticmethod
    def get_branches(directory=os.getcwd()):
        Repository.check_repo(directory)
        work_path = os.path.join(Repository.vcs_path(directory), 'commits')
        branches = list()
        for path in os.listdir(work_path):
            branches.append(path)
        return branches

    @staticmethod
    def add_branch(name, directory=os.getcwd()):
        Repository.check_repo(directory)
        work_path = os.path.join(Repository.vcs_path(directory), 'commits', name)
        if os.path.exists(work_path):
            raise DataError('Branch ' + name + 'already exist')
        os.makedirs(os.path.join(work_path))
        open(os.path.join(work_path, 'CURRENT'), 'tw').close()
        open(os.path.join(work_path, 'HEAD'), 'tw').close()
        open(os.path.join(work_path, 'PARENT'), 'tw').close()

    @staticmethod
    def get_head_commit(branch, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'commits', branch, 'HEAD'), 'r') as f:
            commit = f.read()
            return None if commit == '' else commit

    @staticmethod
    def set_head_commit(branch, commit, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'commits', branch, 'HEAD'), 'w') as f:
            f.seek(0)
            f.write(commit)
            f.truncate()

    @staticmethod
    def get_current_commit(branch, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'commits', branch, 'CURRENT'), 'r') as f:
            commit = f.read()
            return None if commit == '' else commit

    @staticmethod
    def set_current_commit(branch, commit, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'commits', branch, 'CURRENT'), 'w') as f:
            f.seek(0)
            f.write(commit)
            f.truncate()

    @staticmethod
    def get_parent_branch(branch, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'commits', branch, 'PARENT'), 'r') as f:
            try:
                branch, commit = f.read().split(' / ')
            except ValueError as e:
                return None
            return branch, (None if commit == '' else commit)

    @staticmethod
    def set_parent_branch(branch, parent_branch, parent_commit, directory=os.getcwd()):
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'commits', branch, 'PARENT'), 'w') as f:
            f.seek(0)
            data = parent_branch + ' / '
            if parent_commit is not None:
                data += parent_commit
            f.write(data)
            f.truncate()

    @staticmethod
    def save_commit(branch, commit, directory=os.getcwd()):
        work_path = os.path.join(Repository.vcs_path(directory), 'commits', branch, commit.sha)
        if os.path.exists(work_path):
            raise DataError('Commit ' + commit.sha + ' exist')
        with open(work_path, 'w') as f:
            try:
                f.write(commit.save())
            except IOError as e:
                raise RepoError(e)

    @staticmethod
    def load_commit(branch, commit, directory=os.getcwd()):
        work_path = os.path.join(Repository.vcs_path(directory), 'commits', branch,
                                 '' if commit is None else commit)
        if not os.path.exists(work_path):
            raise DataError('Commit not found.')
        if not os.path.isfile(work_path):
            raise InitError('Path ' + work_path + ' is not a file.')
        with open(work_path, 'r') as f:
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

    @staticmethod
    def clear(directory=os.getcwd()):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif not os.path.isdir(file_path) and \
                    os.path.relpath(os.path.abspath(file_path)) != Repository.vcs_path(directory=directory):
                shutil.rmtree(file_path)

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
            Repository.remove(t, os.path.join(directory, tree.name))
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
            fd = open(path, 'w+')
            fd.seek(0)
            fd.write(blob.data)
            fd.truncate()
            fd.close()
        for t in tree.trees:
            path_dir = os.path.join(directory, tree.name, t.name)
            if os.path.exists(path_dir):
                if os.path.isfile(path_dir):
                    os.remove(path_dir)
                    os.mkdir(path_dir)
            else:
                os.mkdir(path_dir)
            Repository.write(t, os.path.join(directory, tree.name))
