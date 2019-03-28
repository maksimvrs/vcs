import unittest

from vcs.diff import Diff


class DiffTests(unittest.TestCase):
    def test_diff(self):
        changes = Diff.diff('qabxcd', 'abycdf')
        print(changes.apply('qabxcd'))
        for change in changes._changes:
            print(change.index,
                  'insert' if change.type == 0 else 'delete', change.data)

    def test_max_match(self):
        self.assertEqual(Diff.max_match('helloabc', 'abctext', 'qwerabctyu'),
                         ((5, 0, 4), 3))
        self.assertEqual(Diff.max_match('qwer', 'tyu', 'iop'), (None, 0))

    def test_diff3(self):
        for i in Diff.diff3('hello\n.'.splitlines(),
                            'hello\n!\nasdfasdf'.splitlines(),
                            'hello\n?\nasdfasdf'.splitlines()):
            print('====================')
            print('Stable' if i.status == 0 else 'Conflict')
            print(i.original)
            print(i.first)
            print(i.second)
            print('====================')

    def test_diff3_empty_original(self):
        for i in Diff.diff3(''.splitlines(),
                            'hello\n!\nasdfasdf'.splitlines(),
                            'hello\n?\nasdfasdf'.splitlines()):
            print('====================')
            print('Stable' if i.status == 0 else 'Conflict')
            print(i.original)
            print(i.first)
            print(i.second)
            print('====================')

    def test_diff3_big_text(self):
        f = open('./tests/data/original_file.txt', 'r')
        data_original = f.read()
        f.close()

        f = open('./tests/data/first_file.txt', 'r')
        data_first = f.read()
        f.close()

        f = open('./tests/data/second_file.txt', 'r')
        data_second = f.read()
        f.close()
        for i in Diff.diff3(data_original.splitlines(),
                            data_first.splitlines(),
                            data_second.splitlines()):

            print('====================')
            print('Stable' if i.status == 0 else 'Conflict')
            print(i.original)
            print(i.first)
            print(i.second)
            print('====================')


if __name__ == '__main__':
    unittest.main()
