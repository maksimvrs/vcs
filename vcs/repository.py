import json
import os
import shutil

from vcs.commit import Commit
from vcs.diff import Diff
from vcs.exceptions import InitError, RepoError, DataError, AddError
from vcs.merge import MergeUnitStatus
from vcs.tree import Tree


class Repository:
    @staticmethod
    def vcs_path(directory=os.getcwd()):
        return os.path.abspath(os.path.join(directory, '.vcs'))

    @staticmethod
    def check_repo(directory=os.getcwd()):
        if not os.path.exists(Repository.vcs_path(directory)):
            raise RepoError('VCS path ' + Repository.vcs_path(directory)
                            + 'not found.')
        if not os.path.exists(os.path.join(Repository.vcs_path(directory),
                                           'INDEXING')):
            raise RepoError('INDEXING file not found.')
        if not os.path.isfile(os.path.join(Repository.vcs_path(directory),
                                           'INDEXING')):
            raise RepoError('INDEXING it is not a file.')
        if not os.path.exists(os.path.join(Repository.vcs_path(directory),
                                           'BRANCH')):
            raise RepoError('BRANCH file not found.')
        if not os.path.isfile(os.path.join(Repository.vcs_path(directory),
                                           'BRANCH')):
            raise RepoError('BRANCH it is not a file.')
        if not os.path.exists(os.path.join(Repository.vcs_path(directory),
                                           'commits')):
            raise RepoError('commits path not found.')
        if not os.path.isdir(os.path.join(Repository.vcs_path(directory),
                                          'commits')):
            raise RepoError('commits it is not a directory.')

    @staticmethod
    def check_branch(branch, directory=os.getcwd()):
        work_path = os.path.join(directory,
                                 Repository.vcs_path(directory),
                                 'commits',
                                 branch)
        if not os.path.exists(work_path):
            raise RepoError(branch + ': Branch path not found.')
        if not os.path.isdir(work_path):
            raise RepoError(branch + ' branch path it is not a directory')
        if not os.path.exists(os.path.join(work_path, 'HEAD')):
            raise RepoError('HEAD file in ' + branch + ' branch not found.')
        if not os.path.isfile(os.path.join(work_path, 'HEAD')):
            raise RepoError('HEAD in ' + branch + ' branch it is '
                            + 'not a file.')
        if not os.path.exists(os.path.join(work_path, 'CURRENT')):
            raise RepoError('CURRENT file in ' + branch + ' branch not found.')
        if not os.path.isfile(os.path.join(work_path, 'CURRENT')):
            raise RepoError('CURRENT in ' + branch + ' branch it is '
                            + 'not a file.')
        if not os.path.exists(os.path.join(work_path, 'PARENT')):
            raise RepoError('PARENT file in ' + branch + ' branch not found.')
        if not os.path.isfile(os.path.join(work_path, 'PARENT')):
            raise RepoError('PARENT in ' + branch + ' branch it is '
                            + 'not a file.')

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
        Repository.check_repo(directory)
        if not os.path.exists(os.path.join(directory, file)):
            raise AddError('File ' + file + ' does not exist.')
        path = os.path.relpath(os.path.abspath(os.path.join(directory, file)),
                               directory)
        with open(os.path.join(Repository.vcs_path(directory), 'INDEXING'),
                  'r+') as f:
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
        Repository.check_repo(directory)
        with open(os.path.join(Repository.vcs_path(directory), 'INDEXING'),
                  'r+') as f:
            try:
                indexing_files = json.load(f)
            except ValueError:
                indexing_files = {}
            if 'files' not in indexing_files:
                return None
            return indexing_files['files']

    @staticmethod
    def clear_indexing(directory=os.getcwd()):
        Repository.check_repo(directory)
        with open(os.path.join(Repository.vcs_path(directory), 'INDEXING'),
                  'r+') as f:
            f.truncate(0)

    @staticmethod
    def get_current_branch(directory=os.getcwd()):
        Repository.check_repo(directory)
        with open(os.path.join(Repository.vcs_path(directory), 'BRANCH'),
                  'r') as f:
            return f.read()

    @staticmethod
    def set_current_branch(branch, directory=os.getcwd()):
        Repository.check_repo(directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory), 'BRANCH'),
                  'w') as f:
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
        work_path = os.path.join(
            Repository.vcs_path(directory), 'commits', name)
        if os.path.exists(work_path):
            raise DataError('Branch ' + name + 'already exist')
        os.makedirs(os.path.join(work_path))
        open(os.path.join(work_path, 'CURRENT'), 'tw').close()
        open(os.path.join(work_path, 'HEAD'), 'tw').close()
        open(os.path.join(work_path, 'PARENT'), 'tw').close()

    @staticmethod
    def remove_branch(branch, directory=os.getcwd()):
        Repository.check_repo(directory)
        shutil.rmtree(os.path.join(Repository.vcs_path(directory),
                                   'commits',
                                   branch))

    @staticmethod
    def get_head_commit(branch, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory),
                               'commits',
                               branch,
                               'HEAD'), 'r') as f:
            commit = f.read()
            return None if commit == '' else commit

    @staticmethod
    def set_head_commit(branch, commit, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory),
                               'commits',
                               branch,
                               'HEAD'), 'w') as f:
            f.seek(0)
            f.write(commit)
            f.truncate()

    @staticmethod
    def get_current_commit(branch, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory),
                               'commits',
                               branch,
                               'CURRENT'), 'r') as f:
            commit = f.read()
            return None if commit == '' else commit

    @staticmethod
    def set_current_commit(branch, commit, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory),
                               'commits',
                               branch,
                               'CURRENT'), 'w') as f:
            f.seek(0)
            f.write(commit)
            f.truncate()

    @staticmethod
    def get_parent_branch(branch, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory),
                               'commits',
                               branch,
                               'PARENT'), 'r') as f:
            try:
                branch, commit = f.read().split(' / ')
            except ValueError:
                return None
            return branch, (None if commit == '' else commit)

    @staticmethod
    def set_parent_branch(branch,
                          parent_branch,
                          parent_commit,
                          directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        if branch not in Repository.get_branches(directory):
            raise DataError('Branch ' + branch + 'not found')
        with open(os.path.join(Repository.vcs_path(directory),
                               'commits',
                               branch,
                               'PARENT'), 'w') as f:
            f.seek(0)
            data = parent_branch + ' / '
            if parent_commit is not None:
                data += parent_commit
            f.write(data)
            f.truncate()

    @staticmethod
    def save_commit(branch, commit, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        work_path = os.path.join(Repository.vcs_path(
            directory), 'commits', branch, commit.sha)
        if os.path.exists(work_path):
            raise DataError('Commit ' + commit.sha + ' exist')
        with open(work_path, 'w') as f:
            try:
                f.write(commit.save())
            except IOError as e:
                raise RepoError(e)

    @staticmethod
    def load_commit(branch, commit, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        work_path = os.path.join(Repository.vcs_path(directory),
                                 'commits',
                                 branch,
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
                commit = Commit(commit_json['parent'],
                                commit_json['author'],
                                commit_json['comment'],
                                commit_json.get('tag'))
                tree = Tree()
                tree.load(commit_json['tree'])
                commit.set(tree)
            except KeyError as e:
                raise DataError('Key ' + str(e) + ' not found')
        return commit

    @staticmethod
    def clear(directory=os.getcwd()):
        Repository.check_repo(directory)
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif not os.path.isdir(file_path) and \
                    os.path.relpath(os.path.abspath(file_path)) != \
                    Repository.vcs_path(directory=directory):
                shutil.rmtree(file_path)

    @staticmethod
    def remove(tree, directory=os.getcwd()):
        Repository.check_repo(directory)
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
            if os.path.exists(path_dir) and \
                    os.path.isdir(path_dir) and \
                    len(os.listdir(path_dir)) == 0:
                os.rmdir(path_dir)

    @staticmethod
    def write(tree, directory=os.getcwd()):
        # Repository.check_repo(directory)
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

    @staticmethod
    def create_merge_file(branch, commit, directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        work_path = os.path.join(Repository.vcs_path(directory),
                                 'commits',
                                 branch)
        with open(os.path.join(work_path, 'MERGE'), 'tw') as f:
            f.seek(0)
            data = Repository.get_current_branch(directory) + ' / ' + commit
            f.write(data)
            f.truncate()

    @staticmethod
    def get_merge_file(branch, directory=os.getcwd()):
        """
        :param branch: branch
        :param directory: directory
        :return: (branch, commit)
        """
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        work_path = os.path.join(Repository.vcs_path(directory),
                                 'commits',
                                 branch)
        if not os.path.exists(os.path.join(work_path, 'MERGE')):
            return None
        with open(os.path.join(work_path, 'MERGE'), 'r') as f:
            try:
                return f.read().split(' / ')
            except ValueError:
                return None

    @staticmethod
    def create_cherry_pick_file(branch, commit_to, commit_from,
                                directory=os.getcwd()):
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        work_path = os.path.join(Repository.vcs_path(directory),
                                 'commits',
                                 branch)
        with open(os.path.join(work_path, 'CHERRY_PICK'), 'tw') as f:
            f.seek(0)
            data = Repository.get_current_branch(directory) + \
                ' / ' + commit_to + ' / ' + commit_from
            f.write(data)
            f.truncate()

    @staticmethod
    def get_cherry_pick_file(branch, directory=os.getcwd()):
        """
        :param branch: branch
        :param directory: directory
        :return: (branch, commit_to, commit_from)
        """
        Repository.check_repo(directory)
        Repository.check_branch(branch, directory)
        work_path = os.path.join(
            Repository.vcs_path(directory), 'commits', branch)
        if not os.path.exists(os.path.join(work_path, 'CHERRY_PICK')):
            return None
        with open(os.path.join(work_path, 'CHERRY_PICK'), 'r') as f:
            try:
                return f.read().split(' / ')
            except ValueError:
                return None

    @staticmethod
    def merge(original_tree, first_tree, second_tree, branch, callback,
              directory=os.getcwd()):
        # Repository.check_repo(directory)
        conflict_blobs = list(set([blob.name for blob in first_tree.blobs])
                              & set([blob.name for blob in second_tree.blobs]))
        other_blobs = list(set([blob.name for blob in first_tree.blobs])
                           ^ set([blob.name for blob in second_tree.blobs]))

        for blob in other_blobs:
            assert (first_tree.name == second_tree.name)
            path = os.path.join(directory, first_tree.name, blob)
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError as e:
                    raise DataError(str(e))
            data = next((b for b in first_tree.blobs +
                         second_tree.blobs if b.name == blob)).data
            fd = open(path, 'w+')
            fd.seek(0)
            fd.write(data)
            fd.truncate()
            fd.close()

        for blob_name in conflict_blobs:
            assert (first_tree.name == second_tree.name)

            original_blob_data = None
            for original_blob in original_tree.blobs:
                if original_blob.name == blob_name:
                    original_blob_data = original_blob.data
                    break
            if original_blob_data is None:
                original_blob_data = ''

            first_blob_data = None
            for first_blob in first_tree.blobs:
                if first_blob.name == blob_name:
                    first_blob_data = first_blob.data
                    break

            second_blob_data = None
            for second_blob in second_tree.blobs:
                if second_blob.name == blob_name:
                    second_blob_data = second_blob.data
                    break

            merge = Diff.diff3(original_blob_data.splitlines(),
                               first_blob_data.splitlines(),
                               second_blob_data.splitlines())
            path = os.path.join(directory, first_tree.name, blob_name)
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError as e:
                    raise DataError(str(e))
            fd = open(path, 'w+')
            fd.seek(0)
            for data in merge:
                if data.status == MergeUnitStatus.Stable:
                    fd.write('\n'.join(data.first) + '\n')
                elif data.status == MergeUnitStatus.Conflict:
                    option = callback((
                        Repository.get_current_branch(directory),
                        '\n'.join(data.original) + '\n'),
                                      (Repository.get_current_branch(
                                          directory), '\n'.join(data.first)
                                                      + '\n'),
                                      (branch, '\n'.join(data.second) + '\n'))
                    if option == 0:
                        fd.write('\n'.join(data.original) + '\n')
                    elif option == 1:
                        fd.write('\n'.join(data.first) + '\n')
                    elif option == 2:
                        fd.write('\n'.join(data.second) + '\n')
            fd.truncate()
            fd.close()
            Repository.add_indexing(path, directory=directory)

        conflict_trees = list(set([tree.name for tree in first_tree.trees])
                              & set([tree.name for tree in second_tree.trees]))
        other_trees = list(set([tree.name for tree in first_tree.trees])
                           ^ set([tree.name for tree in second_tree.trees]))

        for tree in other_trees:
            Repository.write(tree, os.path.join(directory, tree.name))

        for tree in conflict_trees:
            original_tree_data = Tree()
            for original_t in original_tree.trees:
                if original_t.name == tree:
                    original_tree_data = original_t
                    break

            first_tree_data = None
            for first_t in first_tree.trees:
                if first_t.name == tree:
                    first_tree_data = first_t
                    break

            second_tree_data = None
            for second_t in second_tree.trees:
                if second_t.name == tree:
                    second_tree_data = second_t
                    break

            Repository.merge(original_tree_data, first_tree_data,
                             second_tree_data,
                             branch, callback, directory=directory)
