#!/usr/bin/env python

import os
import sys
from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import Cursor
from clang.cindex import CursorKind

header_guard = """#ifndef %(guard)s
#define %(guard)s

#include <gmock/gmock.h>
#include "%(include)s"

%(mock)s
#endif

"""

google_mock = """
class %(base_class)sMock : public %(base_class)s
{
public:
%(methods)s
};

"""

def is_pure_virtual_function(tokens):
    return len(tokens) >= 4 and tokens[0].spelling == 'virtual' and tokens[-3].spelling == '=' and tokens[-2].spelling == '0'

def is_const_function(tokens):
    assert(is_pure_virtual_function(tokens))
    return tokens[-4].spelling == 'const'

def get_result_type(tokens, name):
    assert(is_pure_virtual_function(tokens))
    result_type = []
    for token in tokens[1:]:
        if token.spelling == name:
            break
        result_type.append(token.spelling + ' ')
    return ''.join(result_type)

def format_methods(methods):
    result = []
    first = True
    for method in methods:
        if first:
            first = False
        else:
            result.append('\n')
        result.append('    ' + method)
    return ''.join(result)

def generate_mocks(node, namespace, path):
    mocks = {}
    get_mocks(node, namespace, mocks)

    for base_class, methods in mocks.iteritems():
        if len(methods) > 0:
            class_name = base_class.split("::")[-1]
            mock_class_name = class_name + "Mock.hpp"

            with open(path + "/" + mock_class_name, 'w') as file:
                file.write(header_guard % {
                    'guard' : mock_class_name.replace('.', '_').upper(),
                    'include' : class_name + ".hpp",
                    'mock' : generate_mock(base_class, methods, class_name)
                })

def generate_mock(base_class, methods, class_name):
    mock = []
    for namespace in base_class.split("::")[0 : -1]:
        mock.append("namespace " + namespace + " {" + "\n")
    mock.append(google_mock % { 'base_class' : class_name , 'methods' : format_methods(methods) })
    for namespace in base_class.split("::")[0 : -1]:
        mock.append("} // namespace " + namespace + "\n")
    return ''.join(mock)

def get_mocks(node, namespace, mocks, class_decl = ""):
    if node.kind == CursorKind.CXX_METHOD:
        tokens = list(node.get_tokens())
        if is_pure_virtual_function(tokens):
            mocks.setdefault(class_decl, []).append(
                "MOCK_%(const)sMETHOD%(nr)s(%(name)s, %(result_type)s(%(args)s));" % {
                'const' : is_const_function(tokens) and 'CONST_' or '',
                'nr' : len(list(node.get_arguments())),
                'name' : node.spelling,
                'result_type' : get_result_type(tokens, node.spelling),
                'args' : node.displayname[len(node.spelling) + 1 : -1]
           })
    elif node.kind == CursorKind.CLASS_DECL or node.kind == CursorKind.NAMESPACE:
        class_decl = class_decl == "" and node.displayname or class_decl + (node.displayname == "" and "" or "::") + node.displayname
        if class_decl.startswith(namespace):
            [get_mocks(c, namespace, mocks, class_decl) for c in node.get_children()]
    else:
        [get_mocks(c, namespace, mocks, class_decl) for c in node.get_children()]

def generate_includes(includes):
    result = []
    for inc in includes:
        result.append("#include \"%(include)s\"\n" % { 'include' : inc })
    return ''.join(result)

def parse(files):
    return Index.create(excludeDecls = True).parse(
        path = "~.hpp"
      , unsaved_files = [("~.hpp", generate_includes(files))]
      , options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
    )

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main(args):
    if len(args) < 3:
        print("usage: " + args[0] + " " + "[dir_for_generated_mocks] [limit_to_interfaces_within_namespace]")
        return -1

    create_dir(path = args[1])
    generate_mocks(node = parse(files = args[3:]).cursor, namespace = args[2], path = args[1])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

