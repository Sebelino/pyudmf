#!/usr/bin/env python
import json
from abc import abstractmethod, ABCMeta

import sys
from copy import deepcopy

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

    @abstractmethod
    def __deepcopy__(self, memodict={}):
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

    def __str__(self):
        return "\n\n".join(str(e) for e in self.global_expr_list)

    def __deepcopy__(self, memo={}):
        return TranslationUnit(*[deepcopy(child, memo) for child in self.global_expr_list])


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
        if isinstance(self.value, str) or isinstance(self.value, int):
            value_str = json.dumps(self.value)  # Enforce double quotes
        elif isinstance(self.value, bool):
            value_str = repr(self.value).lower()
        else:
            raise ValueError
        return "{} = {};".format(self.identifier, value_str)

    def __deepcopy__(self, memo={}):
        return Assignment(self.identifier, self.value)


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
        expressions_str = "\n    ".join(str(e) for e in self.expressions)
        return "{} {{\n    {}\n}}".format(self.identifier, expressions_str)

    def __deepcopy__(self, memo={}):
        return Block(self.identifier, deepcopy(self.expressions, memo))


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


def scale(ast, factor: float):
    """ Recursively scales the x and y coordinates of every thing and vertex in the AST. """
    if not isinstance(ast, Node) and not isinstance(ast, list):
        return
    if isinstance(ast, Assignment):
        if ast.identifier in {'x', 'y'}:
            ast.value = str(float(ast.value) * factor)
        return
    for child in ast:
        scale(child, factor)


def scaled(ast: Node, factor: float) -> Node:
    scaled_ast = deepcopy(ast)
    scale(scaled_ast, factor)
    return scaled_ast


if __name__ == '__main__':
    path = sys.argv[1]
    scaling_factor = float(sys.argv[2])
    with open(path, 'r') as f:
        textmap_string = f.read().strip()
    textmap = parse_udmf(textmap_string)
    scale(textmap, scaling_factor)
    print(textmap)
