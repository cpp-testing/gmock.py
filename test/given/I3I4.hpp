#ifndef I3I4_HPP
#define I3I4_HPP

namespace n1 {

struct I3
{
    virtual ~I3() { }

    virtual void f0() {
        f1();
    }

private:
    virtual void f1() = 0;
};

class I4
{
public:
    enum Enum { OK };

    virtual ~I3() { }

    virtual void f0(bool = true) = 0;
    virtual void f1(void) = 0;
    virtual Enum f2()const = 0; // comment
};

#ifdef CLASS_I5
class I5
{
public:
    virtual void f0(void) = 0;
};
#endif

} // namespace n1

#endif

