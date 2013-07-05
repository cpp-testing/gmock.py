#ifndef C1_HPP
#define C1_HPP

namespace n1 {

class C1
{
public:
    explicit C1(int);
    virtual ~C1() { }

    void f0();
    virtual void f1();
    virtual void f2(int) { }
};

} // namespace n1

#endif

