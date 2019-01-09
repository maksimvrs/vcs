import unittest

import hashlib

from vcs.commit import Commit
from vcs.tree import Tree
from vcs.blob import Blob
from vcs.commits_tree import CommitsTree
from vcs.local_interface import LocalInterface


class LocalInterfaceTests(unittest.TestCase):
    def test_init(self):
        LocalInterface.init('./testrepo')

    def test_add_with_dot(self):
        LocalInterface.add('./testrepo/README.md')
        LocalInterface.add('./testrepo/src/main.py')

    def test_add_without_dot(self):
        LocalInterface.add('testrepo/README.md')
        LocalInterface.add('testrepo/src/main.py')
