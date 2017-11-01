#!/usr/bin/env python

from pyparsing import Word, alphas, alphanums, Literal, Combine, Optional, nums, QuotedString, OneOrMore, ZeroOrMore


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
    value = _float | '"' + QuotedString('"') | keyword

    assignment_expr = Optional(identifier + '=' + value + ';')
    expr_list = OneOrMore(assignment_expr)
    block = identifier + '{' + expr_list + '}'
    global_expr = block | assignment_expr
    global_expr_list = OneOrMore(global_expr)
    translation_unit = global_expr_list

    return translation_unit.parseString(textmap_string)


if __name__ == '__main__':
    path = "/home/sebelino/.config/gzdoom/deutex/TEXTMAP.lmp"
    # path = sys.argv[1]
    with open(path, 'r') as f:
        textmap_string = f.read().strip()
    # map = Textmap(textmap_string)
    # print(map)
    textmap_string = """
thing
{
x = 608.000;
y = 256.000;
type = 3001;
angle = 90;
ambush = true;
coop = true;
dm = true;
single = true;
skill1 = true;
skill2 = true;
skill3 = true;
skill4 = true;
skill5 = true;
}
    """
    print(parse_udmf(textmap_string))
