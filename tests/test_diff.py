import unittest

from vcs.diff import Diff


class DiffTests(unittest.TestCase):
    def test(self):
        changes = Diff.diff('qabxcd', 'abycdf')
        print(changes.apply('qabxcd'))
        for change in changes._changes:
            print(change.index,
                  'insert' if change.type == 0 else 'delete', change.data)


if __name__ == '__main__':
    unittest.main()
