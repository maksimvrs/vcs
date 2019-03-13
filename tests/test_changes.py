import unittest

from vcs.diff import Diff


class ChangesTests(unittest.TestCase):
    def test_apply(self):
        changes = Diff.diff("delHerldelo", "Hello!")
        self.assertEqual(changes.apply("delHerldelo"), "Hello!")

    # def test_roll_back(self):
    #     changes = Diff.diff("delHerldelo", "Hello!")
    #     self.assertEqual(changes.roll_back("Hello!"), "delHerldelo")

    def test_many_applt(self):
        changes_1 = Diff.diff(None, 'Hello, world!!!')
        changes_2 = Diff.diff('Hello, world!!!', 'Test program')
        print(changes_1.apply(None))
        print(changes_2.apply(changes_1.apply(None)))

    def test_init(self):
        changes = Diff.diff(None, "Hello!")
        self.assertEqual(changes.apply(None), "Hello!")


if __name__ == '__main__':
    unittest.main()
