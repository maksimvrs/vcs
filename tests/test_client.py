import unittest

import os
import shutil
import json

from vcs.client import Client


class ClientTests(unittest.TestCase):
    PATH = os.path.abspath('../testRepo')

    def setUp(self):
        if os.path.exists(self.PATH):
            if not os.path.isdir(self.PATH):
                os.remove(self.PATH)
                os.mkdir(self.PATH)
            elif os.path.isdir(self.PATH):
                shutil.rmtree(self.PATH)
        os.mkdir(self.PATH)

    def tearDown(self):
        if os.path.exists(self.PATH) and os.path.isdir(self.PATH):
            shutil.rmtree(self.PATH)

    def test_init(self):
        Client.init(self.PATH)

    def test_add(self):
        Client.init(self.PATH)

        open(os.path.join(self.PATH, 'README.md'), 'w').close()

        Client.add('README.md', self.PATH)

        f = open(os.path.join(self.PATH, Client.vcs_path(), 'INDEXING'), 'r')
        indexing_files = json.load(f)
        indexing_files = indexing_files['files']

        self.assertTrue('README.md' in indexing_files)

    def test_commit(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')

        f.write('Hello, world!!!')

        f.close()

        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Inital commit', self.PATH)

    def test_second_commit(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Inital commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Second commit', self.PATH)

    def test_reset(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        sha = Client.commit('Maksim', 'Inital commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Second commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('')
        f.close()
        Client.add('README.md', self.PATH)

        Client.reset(sha, self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'r')
        data = f.read()
        f.close()

        self.assertEqual(data, 'Hello, world!!!')

    def test_reset_second(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Inital commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        sha = Client.commit('Maksim', 'Second commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('')
        f.close()

        Client.reset(sha, self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'r')
        data = f.read()
        f.close()

        self.assertEqual(data, 'New Hello, world!!!')

    def test_log(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Inital commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', self.PATH)

        Client.commit('Maksim', 'Second commit', self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('')
        f.close()


if __name__ == '__main__':
    unittest.main()
