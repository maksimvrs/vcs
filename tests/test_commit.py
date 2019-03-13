import unittest

from vcs.commit import Commit
from vcs.tree import Tree
from vcs.blob import Blob
from vcs.diff import Diff


class CommitTests(unittest.TestCase):
    def test_apply_one_blob(self):
        tree_1 = Tree('/')
        tree_1.blobs.append(Blob('README.md', '1q', 0, Diff.diff(None, 'Hello, world!!!')))

        tree_2 = Tree('/')
        tree_2.blobs.append(Blob('README.md', '2q', 0, Diff.diff('Hello, world!!!', 'Test program')))

        commit_1 = Commit(None, 'Maksim', 'Initial commit')
        commit_1.set(tree_1)

        commit_2 = Commit(commit_1, 'Maksim', 'Second commit')
        commit_2.set(tree_2)

        result = commit_2.apply(commit_1.apply())

        self.assertEqual(result.blobs[0].name, 'README.md')
        self.assertEqual(result.blobs[0].data, 'Test program')


if __name__ == '__main__':
    unittest.main()
