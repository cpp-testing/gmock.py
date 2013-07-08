#!/usr/bin/env python

import os
import sys
from optparse import OptionParser
from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import Cursor
from clang.cindex import CursorKind

class mock_method:
    operators = {
        'operator,'   : 'comma_operator',
        'operator!'   : 'logical_not_operator',
        'operator!='  : 'inequality_operator',
        'operator%'   : 'modulus_operator',
        'operator%='  : 'modulus_assignment_operator',
        'operator&'   : 'address_of_or_bitwise_and_operator',
        'operator&&'  : 'logical_and_operator',
        'operator&='  : 'bitwise_and_assignment_operator',
        'operator()'  : 'function_call_or_cast_operator',
        'operator*'   : 'multiplication_or_dereference_operator',
        'operator*='  : 'multiplication_assignment_operator',
        'operator+'   : 'addition_or_unary_plus_operator',
        'operator++'  : 'increment1_operator',
        'operator+='  : 'addition_assignment_operator',
        'operator-'   : 'subtraction_or_unary_negation_operator',
        'operator--'  : 'decrement1_operator',
        'operator-='  : 'subtraction_assignment_operator',
        'operator->'  : 'member_selection_operator',
        'operator->*' : 'pointer_to_member_selection_operator',
        'operator/'   : 'division_operator',
        'operator/='  : 'division_assignment_operator',
        'operator<'   : 'less_than_operator',
        'operator<<'  : 'left_shift_operator',
        'operator<<=' : 'left_shift_assignment_operator',
        'operator<='  : 'less_than_or_equal_to_operator',
        'operator='   : 'assignment_operator',
        'operator=='  : 'equality_operator',
        'operator>'   : 'greater_than_operator',
        'operator>='  : 'greater_than_or_equal_to_operator',
        'operator>>'  : 'right_shift_operator',
        'operator>>=' : 'right_shift_assignment_operator',
        'operator[]'  : 'array_subscript_operator',
        'operator^'   : 'exclusive_or_operator',
        'operator^='  : 'exclusive_or_assignment_operator',
        'operator|'   : 'bitwise_inclusive_or_operator',
        'operator|='  : 'bitwise_inclusive_or_assignment_operator',
        'operator||'  : 'logical_or_operator',
        'operator~'   : 'complement_operator'
    }

    def __init__(self, result_type, name, is_const, args_size, args, args_prefix = 'arg'):
        self.result_type = result_type
        self.name = name
        self.is_const = is_const
        self.args_size = args_size
        self.args = args
        self.args_prefix = args_prefix

    def __named_args(self):
        result = []
        for i in range(0, self.args_size):
            i and result.append(', ')
            result.append(self.args_prefix + str(i))
        return ''.join(result)

    def __named_args_with_types(self):
        if (self.args == ''):
            return ''
        result = []
        in_type = False
        i = 0
        for c in self.args:
            if c in ['<', '(']:
                in_type = True
            elif c in ['>', ')']:
                in_type = False
            if not in_type and c == ',':
                result.append(' ' + self.args_prefix + str(i))
                i+=1
            result.append(c)
        result.append(' ' + self.args_prefix + str(i))
        return ''.join(result)

    def to_string(self, gap = '    '):
        mock = []
        name = self.name
        if self.name in self.operators:
            mock.append(gap)
            mock.append(
                "virtual %(result_type)s %(name)s(%(args)s) %(const)s{ %(return)s %(body)s; }\n" % {
                    'result_type' : self.result_type,
                    'name' : self.name,
                    'args' : self.__named_args_with_types(),
                    'const' : self.is_const and 'const ' or '',
                    'return' : self.result_type.strip() != 'void' and 'return' or '',
                    'body' : self.operators[self.name] + "(" + self.__named_args() + ")"
                }
            )
            name = self.operators[self.name]

        mock.append(gap)
        mock.append(
            "MOCK_%(const)sMETHOD%(nr)s(%(name)s, %(result_type)s(%(args)s));" % {
            'const' : self.is_const and 'CONST_' or '',
            'nr' : self.args_size,
            'name' : name,
            'result_type' : self.result_type,
            'args' : self.args
        })

        return ''.join(mock)

class mock_generator:
    def __is_const_function(self, tokens):
        for token in reversed(tokens):
            if token.spelling == 'const':
                return True
            elif token.spelling == ')':
                return False
        return False

    def __is_virtual_function(self, tokens):
        return 'virtual' in [token.spelling for token in tokens]

    def __is_pure_virtual_function(self, tokens):
        return len(tokens) >= 3 and                     \
               self.__is_virtual_function(tokens) and   \
               tokens[-3].spelling == '=' and           \
               tokens[-2].spelling == '0' and           \
               tokens[-1].spelling == ';'

    def __get_result_type(self, tokens, name):
        assert(self.__is_pure_virtual_function(tokens))
        result_type = []
        for token in tokens:
            if token.spelling in [name, 'operator']:
                break
            if token.spelling not in ['virtual', 'inline', 'volatile']:
                result_type.append(token.spelling)
            if token.spelling in ['const', 'volatile']:
                result_type.append(' ')
        return ''.join(result_type)

    def __pretty_mock_methods(self, mock_methods):
        result = []
        for i, mock_method in enumerate(mock_methods):
            i and result.append('\n')
            result.append(mock_method.to_string())
            first = False
        return ''.join(result)

    def __pretty_namespaces_begin(self, decl):
        result = []
        for i, namespace in enumerate(decl.split("::")[0 : -1]):
            i and result.append('\n')
            result.append("namespace " + namespace + " {")
        return ''.join(result)

    def __pretty_namespaces_end(self, decl):
        result = []
        for i, namespace in enumerate(decl.split("::")[0 : -1]):
            i and result.append('\n')
            result.append("} // namespace " + namespace)
        return ''.join(result)

    def __get_mock_methods(self, node, mock_methods, class_decl = ""):
        if node.kind == CursorKind.CXX_METHOD:
            tokens = list(node.get_tokens())
            if self.__is_pure_virtual_function(tokens):
                mock_methods.setdefault(class_decl, [node.location.file.name]).append(
                    mock_method(
                         self.__get_result_type(tokens, node.spelling),
                         node.spelling,
                         self.__is_const_function(tokens),
                         len(list(node.get_arguments())),
                         node.displayname[len(node.spelling) + 1 : -1]
                    )
                )
        elif node.kind in [CursorKind.CLASS_DECL, CursorKind.NAMESPACE]:
            class_decl = class_decl == "" and node.displayname \
                or class_decl + (node.displayname == "" and "" or "::") + node.displayname
            if class_decl.startswith(self.decl):
                [self.__get_mock_methods(c, mock_methods, class_decl) for c in node.get_children()]
        else:
            [self.__get_mock_methods(c, mock_methods, class_decl) for c in node.get_children()]

    def __generate_file(self, decl, mock_methods, file_type, file_template_type):
        interface = decl.split("::")[-1]
        mock_file = {
            'hpp' : self.mock_file_hpp % { 'interface' : interface },
            'cpp' : self.mock_file_cpp % { 'interface' : interface },
        }
        path = self.path + "/" + mock_file[file_type]
        not os.path.exists(os.path.dirname(path)) and os.makedirs(os.path.dirname(path))
        with open(path, 'w') as file:
            file.write(file_template_type % {
                'mock_file_hpp' : mock_file['hpp'],
                'mock_file_cpp' : mock_file['cpp'],
                'generated_dir' : self.path,
                'guard' : mock_file[file_type].replace('.', '_').upper(),
                'dir' : os.path.dirname(mock_methods[0]),
                'file' : os.path.basename(mock_methods[0]),
                'namespaces_begin' : self.__pretty_namespaces_begin(decl),
                'interface' : interface,
                'mock_methods' : self.__pretty_mock_methods(mock_methods[1:]),
                'namespaces_end' : self.__pretty_namespaces_end(decl)
            })

    def __init__(self, cursor, decl, path, mock_file_hpp, file_template_hpp, mock_file_cpp, file_template_cpp):
        self.cursor = cursor
        self.decl = decl
        self.path = path
        self.mock_file_hpp = mock_file_hpp
        self.file_template_hpp = file_template_hpp
        self.mock_file_cpp = mock_file_cpp
        self.file_template_cpp = file_template_cpp

    def generate(self):
        mock_methods = {}
        self.__get_mock_methods(self.cursor, mock_methods)
        for decl, mock_methods in mock_methods.iteritems():
            if len(mock_methods) > 0:
                self.file_template_hpp != "" and self.__generate_file(decl, mock_methods, 'hpp', self.file_template_hpp)
                self.file_template_cpp != "" and self.__generate_file(decl, mock_methods, 'cpp', self.file_template_cpp)
        return 0

def main(args):
    def parse(files):
        def generate_includes(includes):
            result = []
            for include in includes:
                result.append("#include \"%(include)s\"\n" % { 'include' : include })
            return ''.join(result)

        return Index.create(excludeDecls = True).parse(
            path = "~.hpp"
          , unsaved_files = [("~.hpp", generate_includes(files))]
          , options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
        )

    parser = OptionParser(usage="usage: %prog [options] files...")
    parser.add_option("-c", "--config", dest="config", default=os.path.dirname(args[0]) + "/gmock.conf", help="config FILE (default='gmock.conf')", metavar="FILE")
    parser.add_option("-d", "--dir", dest="path", default=".", help="dir for generated mocks (default='.')", metavar="DIR")
    parser.add_option("-l", "--limit", dest="decl", default="", help="limit to interfaces within declaration (default='')", metavar="LIMIT")
    (options, args) = parser.parse_args(args)

    if len(args) == 1:
        parser.error("at least one file has to be given")

    config = {}
    execfile(options.config, config)
    return mock_generator(
        cursor = parse(files = args[1:]).cursor,
        decl = options.decl,
        path = options.path,
        mock_file_hpp = config['mock_file_hpp'],
        file_template_hpp = config['file_template_hpp'],
        mock_file_cpp = config['mock_file_cpp'],
        file_template_cpp = config['file_template_cpp']
    ).generate()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

