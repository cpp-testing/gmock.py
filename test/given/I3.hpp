#ifndef I3_HPP
#define I3_HPP

namespace n1 {

class I3
{
public:
    virtual ~I3() { }

    virtual void f0() {
        f1();
    }

private:
    virtual void f1() = 0;
};

class I3
{
public:
    virtual ~I3() { }

    virtual void f0() {
        f1();
    }

private:
    virtual void f1() = 0;
};

} // namespace n1

#endif

