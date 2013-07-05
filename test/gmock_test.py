#!/usr/bin/env python

import os
import sys
import unittest
import shutil
sys.path.append('..')
import gmock

def read_file(path):
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

class TestGMock(unittest.TestCase):
    generated_dir = 'generated'

    def assertMocks(self):
        for file in os.listdir(self.generated_dir):
            self.assertEqual(read_file(self.generated_dir + '/' + file), read_file('then/' + file))

    def setUp(self):
        shutil.rmtree(path = self.generated_dir, ignore_errors = True)

    def tearDown(self):
        shutil.rmtree(path = self.generated_dir, ignore_errors = True)

    def test_gmock_args_fail_none(self):
        self.assertEqual(-1, gmock.main(['']))

    def test_gmock_args_fail_file_not_found(self):
        self.assertEqual(0, gmock.main(['', '../gmock.conf', self.generated_dir, '', 'not_found.hpp' ]))

    def test_gmock_one_file_no_output(self):
        self.assertEqual(0, gmock.main(['', '../gmock.conf', self.generated_dir, 'n1', 'given/I1.hpp']))
        self.assertEqual(0, len([name for name in os.listdir(self.generated_dir)]))

    def test_gmock_one_file_with_output(self):
        self.assertEqual(0, gmock.main(['', '../gmock.conf', self.generated_dir, 'n1', 'given/I2.hpp']))
        self.assertEqual(1, len([name for name in os.listdir(self.generated_dir)]))
        self.assertTrue('I2Mock.hpp' in os.listdir(self.generated_dir))
        self.assertMocks();

    def test_gmock_many_files(self):
        self.assertEqual(0, gmock.main(['', '../gmock.conf', self.generated_dir, 'n1', 'given/I1.hpp', 'given/I2.hpp', 'given/I3I4.hpp', 'given/C1.hpp']))
        self.assertEqual(3, len([name for name in os.listdir(self.generated_dir)]))
        self.assertTrue('I2Mock.hpp' in os.listdir(self.generated_dir))
        self.assertTrue('I3Mock.hpp' in os.listdir(self.generated_dir))
        self.assertTrue('I4Mock.hpp' in os.listdir(self.generated_dir))
        self.assertMocks();

    def test_gmock_custom_conf(self):
        self.assertEqual(0, gmock.main(['', 'test.conf', self.generated_dir, 'n1', 'given/I2.hpp']))
        self.assertEqual(1, len([name for name in os.listdir(self.generated_dir)]))
        self.assertTrue('I2_mock.hpp' in os.listdir(self.generated_dir))
        self.assertMocks();

if __name__ == '__main__':
    unittest.main()

