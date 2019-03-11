import unittest

import os

from vcs.client import Client
from vcs.commit import Commit
from vcs.tree import Tree
from vcs.blob import Blob
from vcs.diff import Diff


class ClientTests(unittest.TestCase):
    def test_init(self):
        Client.init('/Users/maksim/Projects/VCS/testRepo')

    def test_add(self):
        Client.add('README.md', '/Users/maksim/Projects/VCS/testRepo')

    def test_commit(self):
        Client.commit('Maksim', 'Inital commit', '/Users/maksim/Projects/VCS/testRepo')

    def test_second_commit(self):
        Client.commit('Maksim', 'Second commit', '/Users/maksim/Projects/VCS/testRepo')
