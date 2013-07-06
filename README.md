**Google Mock** mocks generator based on libclang

### Requirements
 + [python](http://www.python.org) (tested with 2.7 and 3.2)
 + [libclang](http://clang.llvm.org) (tested with 3.2)

### Download
```
git clone --recursive git@github.com:krzysztof-jusiak/gmock.git
```

### Usage
```
Usage: gmock.py [options] files...

Options:
  -h, --help                show this help message and exit
  -c FILE, --config=FILE    config FILE (default='gmock.conf')
  -d DIR, --dir=DIR         dir for generated mocks (default='.')
  -l LIMIT, --limit=LIMIT   limit to interfaces within declaration (default='')
```

### Example
```
./gmock.py file.hpp
```
will create mocks files in current directory for all interfaces

```
./gmock.py -c "gmock.conf" -d "test/mocks" -l "namespace::class" file1.hpp file2.hpp
```
will create directory 'test/mocks' and mocks files within this directory for all interfaces (contains at least one pure virtual function)
which will be within 'namespace::class' declaration

### Integration with build system
```
find project -iname "*.h" -or -iname "*.hpp" | xargs\
"projects/externals/gmock.py" -c "project/conf/gmock.conf" -d "project/generated/mocks" -l "Project"
```

### Features
 + it's reliable (based on clang compiler)
 + it's fast (tested on project ~200 kloc -> generation of mocs takes 3-5s on common laptop)
 + output file might be easily adopted to the project via configuration file
 + easy integration with the project build system -> generate mocks files for each interface, limited to the project (for example via project namespace), from given files
 + generate pretty output (one mock per file)
 + easy to extend (~200 lines of code)
 + handle c++ operators

```
    virtual int operator()(int, double) = 0;
```

```
    virtual int operator()(int arg0, double arg1) { return call_operator(arg0, arg1); }
    MOCK_METHOD2(call_operator, int(int, double));
```

### Configuration file
```
#vars:
# file: interface file name
# dir: interface directory
# guard: header guard
# interface: interface class
# mock_methods: generated gmock methods

mock_file = "%(interface)sMock.hpp"

file_template="""\
/*
 * file generated by gmock: %(mock_file)s
 */
#ifndef %(guard)s
#define %(guard)s

#include <gmock/gmock.h>
#include "%(dir)s/%(file)s"

%(namespaces_begin)s

class %(interface)sMock : public %(interface)s
{
public:
%(mock_methods)s
};

%(namespaces_end)s

#endif // %(guard)s

"""
```
