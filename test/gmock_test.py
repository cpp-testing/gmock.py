#!/usr/bin/env python

import os
import sys
import unittest
import shutil
sys.path.append('..')
import gmock

t2_mock="""#ifndef T2MOCK_HPP
#define T2MOCK_HPP

#include <gmock/gmock.h>
#include "T2.hpp"

namespace n1 {

class T2Mock : public T2
{
public:
    MOCK_CONST_METHOD0(f0, void());
    MOCK_METHOD1(f1, void(int));
    MOCK_METHOD1(f2, void(double));
    MOCK_METHOD2(f3, void(int, double));
    MOCK_METHOD3(f4, void(int, double, const std::string &));
    MOCK_METHOD1(f5, int(const std::string &));
    MOCK_CONST_METHOD1(f6, boost::shared_ptr<int>(const boost::shared_ptr<int> &));
    MOCK_CONST_METHOD0(f7, const int&());
    MOCK_METHOD0(f8, boost::function<void(int)>());
    MOCK_CONST_METHOD2(f9, boost::non_type<int,0>(const boost::non_type<int, 1> &, const boost::non_type<int, 2> &));
    MOCK_METHOD0(f10, const int*const ());
    virtual int operator()( arg0) { return call_operator(); }
    MOCK_METHOD0(call_operator, int());
    virtual void operator()(int arg0, double arg1, boost::function<void (int, double)> arg2, const boost::non_type<int, 1> & arg3, const std::string & arg4) {  call_operator(arg0, arg1, arg2, arg3, arg4); }
    MOCK_METHOD5(call_operator, void(int, double, boost::function<void (int, double)>, const boost::non_type<int, 1> &, const std::string &));
    virtual double operator[](int arg0) { return subscript_operator(arg0); }
    MOCK_METHOD1(subscript_operator, double(int));
};

} // namespace n1

#endif

"""

c2_mock = """#ifndef C2MOCK_HPP
#define C2MOCK_HPP

#include <gmock/gmock.h>
#include "C2.hpp"

namespace n1 {
namespace  {

class C2Mock : public C2
{
public:
    MOCK_METHOD0(f1, void());
};

} // namespace n1
} // namespace 

#endif

"""

def read_file(path):
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

class TestGMock(unittest.TestCase):
    generated_dir = 'generated'

    def setUp(self):
        shutil.rmtree(path = self.generated_dir, ignore_errors = True)

    def tearDown(self):
        shutil.rmtree(path = self.generated_dir, ignore_errors = True)

    def test_gmock_args_fail(self):
        self.assertEqual(-1, gmock.main(['']))

    def test_gmock_args_fail(self):
        self.assertEqual(0, gmock.main(['', self.generated_dir, '', 'not_found.hpp' ]))

    def test_gmock_success(self):
        self.assertEqual(0, gmock.main(['', self.generated_dir, 'n1', 'test.hpp']))
        self.assertEqual(2, len([name for name in os.listdir(self.generated_dir)]))
        self.assertEqual('T2Mock.hpp', os.listdir(self.generated_dir)[0])
        self.assertEqual('C2Mock.hpp', os.listdir(self.generated_dir)[1])
        self.assertEqual(t2_mock, read_file(self.generated_dir + '/T2Mock.hpp'))
        self.assertEqual(c2_mock, read_file(self.generated_dir + '/C2Mock.hpp'))

if __name__ == '__main__':
    unittest.main()

