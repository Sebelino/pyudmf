#!/usr/bin/env python
from abc import abstractmethod, ABCMeta

from pyparsing import Word, alphas, alphanums, Literal, Combine, Optional, nums, QuotedString, ZeroOrMore, \
    Group


class Node(metaclass=ABCMeta):
    def __eq__(self, other):
        return self.__class__ == other.__class__ and all(a == b for a, b in zip(self, other))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join(repr(c) for c in self))

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def group(cls, expr):
        raise NotImplementedError


class TranslationUnit(Node):
    def __init__(self, *lst):
        self.global_expr_list = lst

    def __getitem__(self, i):
        return self.global_expr_list[i]

    @classmethod
    def group(cls, expr):
        def group_action(s, l, t):
            lst = t[0].asList()
            return cls(*lst)
        return Group(expr).setParseAction(group_action)


class Assignment(Node):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def __getitem__(self, i):
        children = [self.identifier, self.value]
        return children[i]

    @classmethod
    def group(cls, expr):
        def group_action(s, l, t):
            lst = t[0].asList()
            identifier, _, value, _ = lst
            return cls(identifier, value)

        return Group(expr).setParseAction(group_action)

    def __str__(self):
        return "{} = {};".format(self.identifier, self.value)


class Block(Node):
    def __init__(self, identifier: str, expressions: list):
        self.identifier = identifier
        self.expressions = expressions

    def __getitem__(self, i):
        children = [self.identifier, self.expressions]
        return children[i]

    @classmethod
    def group(cls, expr):
        def group_action(s, l, t):
            lst = t[0].asList()
            identifier = lst[0]
            expressions = lst[2:-1]
            return cls(identifier, expressions)
        return Group(expr).setParseAction(group_action)

    def __str__(self):
        expressions_str = " ".join(e for e in self.expressions)
        return "{} {{}}".format(self.identifier, expressions_str)


def parse_udmf(textmap_string: str):
    """
    translation_unit := global_expr_list
    global_expr_list := global_expr global_expr_list
    global_expr := block | assignment_expr
    block := identifier '{' expr_list '}'
    expr_list := assignment_expr expr_list
    assignment_expr := identifier '=' value ';' | nil
    identifier := [A-Za-z_]+[A-Za-z0-9_]*
    value := integer | float | quoted_string | keyword
    integer := [+-]?[1-9]+[0-9]* | 0[0-9]+ | 0x[0-9A-Fa-f]+
    float := [+-]?[0-9]+'.'[0-9]*([eE][+-]?[0-9]+)?
    quoted_string := "([^"\\]*(\\.[^"\\]*)*)"
    keyword := [^{}();"'\n\t ]+

    :param textmap_string:
    :return: pyparsing instance parsed from @textmap_string
    """
    _plusorminus = Literal('+') | Literal('-')
    identifier = Word(alphas + '_', alphanums + '_')
    _uinteger = Word(nums)
    # TODO hexadecimal, octal integers
    _integer = Combine(Optional(_plusorminus) + _uinteger)
    _float = Combine(_integer + Optional(Literal('.') + Optional(_uinteger)))
    keyword = Word(alphas)  # [^{}();"'\n\t ]+
    value = _float | QuotedString('"') | keyword

    assignment_expr = Assignment.group(identifier + '=' + value + ';')
    expr_list = ZeroOrMore(assignment_expr)
    block = Block.group(identifier + '{' + expr_list + '}')
    global_expr = block | assignment_expr
    global_expr_list = ZeroOrMore(global_expr)
    translation_unit = TranslationUnit.group(global_expr_list)

    ast = translation_unit.parseString(textmap_string)[0]
    return ast


if __name__ == '__main__':
    path = "/home/sebelino/.config/gzdoom/deutex/TEXTMAP.lmp"
    # path = sys.argv[1]
    with open(path, 'r') as f:
        textmap_string = f.read().strip()
    # map = Textmap(textmap_string)
    # print(map)
    textmap_string = """
namespace = "zdoom";
    """
    ast = parse_udmf(textmap_string)
    print(ast)
