import unittest

from vcs.diff import Diff


class DiffTests(unittest.TestCase):
    def test(self):
        changes = Diff.diff("delHerldelo", "Hello!")
        print(changes._changes)
