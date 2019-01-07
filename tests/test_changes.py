import unittest

from vcs.diff import Diff


class ChangesTests(unittest.TestCase):
    def test_apply(self):
        changes = Diff.diff("delHerldelo", "Hello!")
        self.assertEqual(changes.apply("delHerldelo"), "Hello!")

    def test_roll_back(self):
        changes = Diff.diff("delHerldelo", "Hello!")
        self.assertEqual(changes.roll_back("Hello!"), "delHerldelo")
