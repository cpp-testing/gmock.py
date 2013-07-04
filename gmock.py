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
%(mock_methods)s
};

"""

class mock_method:
    def __init__(self, result_type, name, is_const, args_size, args):
        self.result_type = result_type
        self.name = name
        self.is_const = is_const
        self.args_size = args_size
        self.args = args

    def to_string(self):
        return \
            "MOCK_%(const)sMETHOD%(nr)s(%(name)s, %(result_type)s(%(args)s));" % {
            'const' : self.is_const and 'CONST_' or '',
            'nr' : self.args_size,
            'name' : self.name,
            'result_type' : self.result_type,
            'args' : self.args
        }

class mock_generator:
    def __is_virtual_function(self, tokens):
        return len(tokens) >= 0 and tokens[0].spelling == 'virtual'

    def __is_pure_virtual_function(self, tokens):
        return len(tokens) >= 4 and                     \
               self.__is_virtual_function(tokens) and   \
               tokens[-3].spelling == '=' and           \
               tokens[-2].spelling == '0'

    def __is_const_function(self, tokens):
        assert(self.__is_pure_virtual_function(tokens))
        return tokens[-4].spelling == 'const'

    def __get_result_type(self, tokens, name):
        assert(self.__is_pure_virtual_function(tokens))
        result_type = []
        for token in tokens[1:]:
            if token.spelling == name:
                break
            result_type.append(token.spelling + ' ')
        return ''.join(result_type)

    def __format_mock_methods(self, mock_methods):
        result = []
        first = True
        for mock_method in mock_methods:
            not first and result.append('\n')
            result.append('    ' + mock_method.to_string())
            first = False
        return ''.join(result)

    def __generate_mock(self, base_class, mock_methods, class_name):
        mock = []
        for namespace in base_class.split("::")[0 : -1]:
            mock.append("namespace " + namespace + " {" + "\n")
        mock.append(self.google_mock % {
            'base_class' : class_name,
            'mock_methods' : self.__format_mock_methods(mock_methods)
        })
        for namespace in base_class.split("::")[0 : -1]:
            mock.append("} // namespace " + namespace + "\n")
        return ''.join(mock)

    def __get_mock_methods(self, node, mock_methods, class_decl = ""):
        if node.kind == CursorKind.CXX_METHOD:
            tokens = list(node.get_tokens())
            if self.__is_pure_virtual_function(tokens):
                mock_methods.setdefault(class_decl, []).append(
                    mock_method(
                         self.__get_result_type(tokens, node.spelling),
                         node.spelling,
                         self.__is_const_function(tokens),
                         len(list(node.get_arguments())),
                         node.displayname[len(node.spelling) + 1 : -1]
                    )
                )
        elif node.kind == CursorKind.CLASS_DECL or node.kind == CursorKind.NAMESPACE:
            class_decl = class_decl == "" and node.displayname \
                or class_decl + (node.displayname == "" and "" or "::") + node.displayname
            if class_decl.startswith(self.decl):
                [self.__get_mock_methods(c, mock_methods, class_decl) for c in node.get_children()]
        else:
            [self.__get_mock_methods(c, mock_methods, class_decl) for c in node.get_children()]

    def __init__(self, cursor, decl, path, header_guard = header_guard, google_mock = google_mock):
        self.cursor = cursor
        self.decl = decl
        self.path = path
        self.header_guard = header_guard
        self.google_mock = google_mock

    def generate(self):
        mock_methods = {}
        self.__get_mock_methods(self.cursor, mock_methods)
        for base_class, mock_methods in mock_methods.iteritems():
            if len(mock_methods) > 0:
                class_name = base_class.split("::")[-1]
                mock_class_name = class_name + "Mock.hpp"
                with open(self.path + "/" + mock_class_name, 'w') as file:
                    file.write(self.header_guard % {
                        'guard' : mock_class_name.replace('.', '_').upper(),
                        'include' : class_name + ".hpp",
                        'mock' : self.__generate_mock(base_class, mock_methods, class_name)
                    })

def main(args):
    def create_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def parse(files):
        def generate_includes(includes):
            result = []
            for inc in includes:
                result.append("#include \"%(include)s\"\n" % { 'include' : inc })
            return ''.join(result)

        return Index.create(excludeDecls = True).parse(
            path = "~.hpp"
          , unsaved_files = [("~.hpp", generate_includes(files))]
          , options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
        )

    if len(args) < 3:
        print("usage: " + args[0] + " [dir_for_generated_mocks] [limit_to_interfaces_within_decl]")
        return -1

    create_dir(path = args[1])
    mock_generator(cursor = parse(files = args[3:]).cursor, decl = args[2], path = args[1]).generate()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

