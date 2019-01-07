import unittest

from vcs.commit import Commit
from vcs.tree import Tree
from vcs.blob import Blob
from vcs.diff import Diff


class CommitTests(unittest.TestCase):
    def test_apply_one_blob(self):
        commit_tree = Tree('/')
        commit_tree.blobs.append(Blob('README.md', '', 0, Diff.diff('Program', 'Test program')))

        tree = Tree('/')
        tree.blobs.append(Blob('README.md', '', 0, None, 'Program'))

        commit = Commit(None, "Initial commit")
        commit.set(commit_tree)
        result = commit.apply(tree)

        self.assertEqual(result.blobs[0].name, 'README.md')
        self.assertEqual(result.blobs[0].data(), 'Test program')

    def test_roll_back_one_blob(self):
        commit_tree = Tree('/')
        commit_tree.blobs.append(Blob('README.md', '', 0, Diff.diff('Program', 'Test program')))

        tree = Tree('/')
        tree.blobs.append(Blob('README.md', '', 0, None, 'Test program'))

        commit = Commit(None, "Initial commit")
        commit.set(commit_tree)
        result = commit.roll_back(tree)

        self.assertEqual(result.blobs[0].name, 'README.md')
        self.assertEqual(result.blobs[0].data(), 'Program')
