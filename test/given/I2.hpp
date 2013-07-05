#ifndef I2_HPP
#define I2_HPP

#include <boost/shared_ptr.hpp>
#include <boost/function.hpp>
#include <boost/non_type.hpp>

namespace n1 {

class I2
{
public:
    virtual ~I2();

    virtual void f0()const=0;

    virtual void f1(
        int
    ) = 0;

    virtual void f2(double) = 0;
    virtual void f3(int, double) = 0;
    virtual void f4(int i, double d, const std::string& str) = 0;
    virtual int f5(const std::string& str) = 0;
    virtual boost::shared_ptr<int> f6(const boost::shared_ptr<int>&) const = 0;
    virtual const int& f7() const = 0;
    virtual boost::function<void(int)> f8() = 0;
    virtual boost::non_type<int, 0> f9(const boost::non_type<int, 1>&, const boost::non_type<int, 2>&) const = 0;
    virtual const int * const f10() = 0;

    inline virtual const void f11() = 0;
    virtual inline const void f12() = 0;
    virtual const void f13() = 0;
    const virtual void f14() = 0;
    volatile const virtual void f15() = 0;
    const virtual volatile void f16() = 0;
    const virtual volatile inline void f17() = 0;

    virtual int operator()() = 0;
    virtual void operator()(int, double d, boost::function<void(int, double)>, const boost::non_type<int, 1>&, const std::string& str) = 0;
    virtual double operator[](int) = 0;
    virtual void* operator->() const = 0;
};

} // namespace n1

#endif

