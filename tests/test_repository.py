import unittest

import os
import shutil
import json

from vcs.blob import Blob
from vcs.commit import Commit
from vcs.diff import Diff
from vcs.repository import Repository
from vcs.tree import Tree


class RepositoryTests(unittest.TestCase):
    PATH = os.path.abspath('../testRepo')

    def setUp(self):
        if os.path.exists(self.PATH):
            if not os.path.isdir(self.PATH):
                os.remove(self.PATH)
                os.mkdir(self.PATH)
            elif os.path.isdir(self.PATH):
                shutil.rmtree(self.PATH)
        os.mkdir(self.PATH)

    def tearDown(self):
        if os.path.exists(self.PATH) and os.path.isdir(self.PATH):
            shutil.rmtree(self.PATH)

    def test_init(self):
        Repository.init(directory=self.PATH)

    def test_add_indexing(self):
        Repository.init(directory=self.PATH)

        open(os.path.join(self.PATH, 'README.md'), 'w').close()

        Repository.add_indexing('README.md', directory=self.PATH)

        f = open(os.path.join(Repository.vcs_path(self.PATH), 'INDEXING'), 'r')
        indexing_files = json.load(f)
        indexing_files = indexing_files['files']

        self.assertTrue('README.md' in indexing_files)

    def test_get_indexing(self):
        Repository.init(directory=self.PATH)

        open(os.path.join(self.PATH, 'README.md'), 'w').close()
        open(os.path.join(self.PATH, 'LICENSE'), 'w').close()

        Repository.add_indexing('README.md', directory=self.PATH)
        Repository.add_indexing('LICENSE', directory=self.PATH)

        files = Repository.get_indexing(directory=self.PATH)

        self.assertTrue('README.md' in files)
        self.assertTrue('LICENSE' in files)

    def test_create_branch(self):
        Repository.init(directory=self.PATH)

        Repository.add_branch('develop', directory=self.PATH)

    def test_save_commit(self):
        Repository.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')

        f.write('Hello, world!!!')

        f.close()

        Repository.add_indexing('README.md', directory=self.PATH)

        tree = Tree('/')
        tree.blobs.append(Blob('README.md', '1q', 0,
                               Diff.diff(None, 'Hello, world!!!')))
        commit = Commit(None, 'Maksim', 'Initial commit')
        commit.set(tree)

        Repository.save_commit('master', commit, directory=self.PATH)
        Repository.set_head_commit('master', commit.sha, directory=self.PATH)
        Repository.set_current_commit('master',
                                      commit.sha,
                                      directory=self.PATH)

    def test_commit_to_branch(self):
        Repository.init(directory=self.PATH)

        Repository.add_branch('develop', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')

        f.write('Hello, world!!!')

        f.close()

        Repository.add_indexing('README.md', directory=self.PATH)

        tree = Tree('/')
        tree.blobs.append(Blob('README.md', '1q', 0,
                               Diff.diff(None, 'Hello, world!!!')))
        commit = Commit(None, 'Maksim', 'Initial commit')
        commit.set(tree)

        Repository.save_commit('develop', commit, directory=self.PATH)
        Repository.set_head_commit('develop', commit.sha, directory=self.PATH)
        Repository.set_current_commit('develop',
                                      commit.sha,
                                      directory=self.PATH)


if __name__ == '__main__':
    unittest.main()
