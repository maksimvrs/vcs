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
        Client.init(directory=self.PATH)

    def test_add(self):
        Client.init(directory=self.PATH)

        open(os.path.join(self.PATH, 'README.md'), 'w').close()

        Client.add('README.md', directory=self.PATH)

        f = open(os.path.join(self.PATH, Client.vcs_path(), 'INDEXING'), 'r')
        indexing_files = json.load(f)
        indexing_files = indexing_files['files']

        self.assertTrue('README.md' in indexing_files)

    def test_commit(self):
        Client.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        commit = Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, '.vcs/commits/master', commit), 'r')
        data = json.load(f)
        f.close()

        expext_data = {
            'author': 'Maksim',
            'comment': 'Inital commit',
            'parent': None,
            'tag': 'Inital commit',
            'tree': {
                'blobs': [
                    {
                        'changes': [
                            {
                                'data': 'Hello, world!!!',
                                'index': 0,
                                'type': 0}
                        ],
                        'name': 'README.md',
                        'sha': '91a93333a234aa14b2386dee4f644579c64c29a1',
                        'size': 15
                    }
                ],
                'name': '.',
                'trees': []
            }
        }
        self.assertDictEqual(data, expext_data)

    def test_second_commit(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.commit('Maksim', 'Second commit', directory=self.PATH)

    def test_commit_with_subdirs(self):
        Client.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()

        os.mkdir(os.path.join(self.PATH, 'src'))
        f = open(os.path.join(self.PATH, 'src', 'main.txt'), 'w')
        f.write('Main src file')
        f.close()

        Client.add('README.md', directory=self.PATH)
        Client.add('src/main.txt', directory=self.PATH)

        Client.commit('Maksim', 'Inital commit', directory=self.PATH)

    def test_reset(self):
        Client.init(self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        sha = Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.commit('Maksim', 'Second commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.reset(sha, directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'r')
        data = f.read()
        f.close()

        self.assertEqual(data, 'Hello, world!!!')

    def test_reset_second(self):
        Client.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        sha = Client.commit('Maksim', 'Second commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('')
        f.close()

        Client.reset(sha, directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'r')
        data = f.read()
        f.close()

        self.assertEqual(data, 'New Hello, world!!!')

    def test_log(self):
        Client.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, world!!!')
        f.close()
        Client.add('README.md', directory=self.PATH)

        Client.commit('Maksim', 'Second commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('')
        f.close()

    def test_create_branch(self):
        Client.init(directory=self.PATH)

        Client.branch('develop', directory=self.PATH)
        Client.checkout('develop', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        Client.commit('Maksim', 'Inital commit', directory=self.PATH)

    def test_checkout(self):
        Client.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world from master!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        Client.branch('develop', directory=self.PATH)
        Client.checkout('develop', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, world from develop!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        Client.commit('Maksim', 'Commit to develop branch', directory=self.PATH)

        Client.checkout('master', directory=self.PATH)

    def test_checkout_after_reset(self):
        Client.init(directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, World!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        initial_commit = Client.commit('Maksim', 'Inital commit', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('New Hello, World!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        Client.commit('Maksim', 'Second commit', directory=self.PATH)

        Client.branch('develop', directory=self.PATH)
        Client.checkout('develop', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'w')
        f.write('Hello, World from developer!!!')
        f.close()

        Client.add('README.md', directory=self.PATH)
        Client.commit('Maksim', 'Commit to develop branch', directory=self.PATH)

        Client.checkout('master', directory=self.PATH)

        Client.reset(initial_commit, directory=self.PATH)
        Client.checkout('develop', directory=self.PATH)

        f = open(os.path.join(self.PATH, 'README.md'), 'r')
        data = f.read()

        self.assertEqual(data, 'Hello, World from developer!!!')


if __name__ == '__main__':
    unittest.main()
