#ifndef TEST1_HPP
#define TEST1_HPP

#include <boost/shared_ptr.hpp>
#include <boost/function.hpp>
#include <boost/non_type.hpp>

class T1
{
public:
    virtual ~T1();

    virtual void f() = 0;
};

namespace n1 {

class T2
{
public:
    virtual ~T2();

    virtual void f0() const = 0;
    virtual void f1(int) = 0;
    virtual void f2(double) = 0;
    virtual void f3(int, double) = 0;
    virtual void f4(int i, double d, const std::string& str) = 0;
    virtual int f5(const std::string& str) = 0;
    virtual boost::shared_ptr<int> f6(const boost::shared_ptr<int>&) const = 0;
    virtual const int& f7() const = 0;
    virtual boost::function<void(int)> f8() = 0;
    virtual boost::non_type<int, 0> f9(const boost::non_type<int, 1>&, const boost::non_type<int, 2>&) const = 0;
    virtual int operator()() = 0;
};

namespace n2 {

class C1
{
public:
    explicit C1(int);

    void f0();
    virtual void f1();
    virtual void f2(int) { }
};

} // namespace n2

namespace {

class C2
{
public:
    virtual void f0() {
        f1();
    }

private:
    virtual void f1() = 0;
};

} // namespace
} // namespace n1

#endif

