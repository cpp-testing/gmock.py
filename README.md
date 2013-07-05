**Google Mock** mocks generator based on libclang

### Download
```
    git clone --recursive git@github.com:krzysztof-jusiak/gmock.git
```
### Requirements
 + [python](http://www.python.org)
 + [libclang](http://clang.llvm.org)

### Usage
```
./gmock.py <directory> <limit_to_interfaces_within_decl> files...
```

### Example
```
./gmock.py "test/mocks" "namespace::class" file1.hpp file2.hpp
```
will create directory 'test/mocks' and mocks within this directory for all interfaces (contains at least one pure virtual function)
which will be within 'namespace::class' declaration:
 + test/mocks//file1Mock.hpp
 + test/mocks/file2Mock.hpp

