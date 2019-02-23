import unittest

import hashlib

from vcs.commit import Commit
from vcs.tree import Tree
from vcs.blob import Blob
from vcs.diff import Diff
from vcs.commits_tree import CommitsTree


class CommitsTreeTests(unittest.TestCase):
    def test_get_data(self):
        tree_1 = Tree('/')
        tree_1.blobs.append(Blob('README.md', hashlib.sha1('1q2317d'.encode()), 0, Diff.diff('', 'Program')))

        commit_1 = Commit(None, 'Maksim', "Initial commit")
        commit_1.set(tree_1)

        tree_2 = Tree('/')
        tree_2.blobs.append(Blob('README.md', hashlib.sha1('2q2317d'.encode()), 0, Diff.diff('Program', 'Test program')))

        commit_2 = Commit(None, 'Maksim', "Second commit")
        commit_2.set(tree_2)

        commits_tree = CommitsTree()
        commits_tree.add(commit_1)
        commits_tree.add(commit_2)

        self.assertEqual(commits_tree.get_data(commit_1.sha).blobs[0].name, 'README.md')
        self.assertEqual(commits_tree.get_data(commit_1.sha).blobs[0].apply(), 'Program')

        self.assertEqual(commits_tree.get_data(commit_2.sha).blobs[0].name, 'README.md')
        self.assertEqual(commits_tree.get_data(commit_2.sha).blobs[0].apply(), 'Test program')
