import string
from enum import Enum
from typing import List, Optional, Union, Tuple


class Token(Enum):
    AND = '&'
    OR = '|'
    XOR = '^'
    NOT = '!'
    IMPL = '=>'
    EQ = '=='
    CONST_0 = '0'
    CONST_1 = '1'
    PAREN_LEFT = '('
    PAREN_RIGHT = ')'

    def __str__(self):
        return self.value


class VarToken:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'${self.name}'


TokenList = List[Union[Token, VarToken]]


def _tokenize(expr: str) -> Optional[TokenList]:
    results = []

    i = 0
    while i < len(expr):
        if expr[i] == ' ':
            i += 1
            continue

        matched = False
        for token in Token:
            text = token.value
            if i + len(text) <= len(expr) and text == expr[i:i + len(text)]:
                i += len(text)
                results.append(token)
                matched = True
                break
        if matched:
            continue

        if expr[i] in string.ascii_letters:
            begin = i

            while i < len(expr) and expr[i] in string.ascii_letters:
                i += 1

            text = expr[begin:i]
            results.append(VarToken(text))
            continue

        return None

    return results


def _validate(expr: TokenList) -> bool:
    state = 1
    parentheses = 0

    for token in expr:
        if state == 1:
            if token == Token.PAREN_LEFT:
                parentheses += 1
            elif token == Token.NOT:
                pass
            elif type(token) is VarToken or token in [Token.CONST_0, Token.CONST_1]:
                state = 2
            else:
                return False
        else:
            if token == Token.PAREN_RIGHT:
                parentheses -= 1
                if parentheses < 0:
                    return False
            elif token in [Token.AND, Token.OR, Token.XOR, Token.IMPL, Token.EQ]:
                state = 1
            else:
                return False

    return state == 2 and parentheses == 0


def _extract_variables(expr: TokenList) -> List[str]:
    return sorted(set(token.name for token in expr if type(token) is VarToken))


def _infix_to_rpn(expr: TokenList) -> TokenList:
    priorities = {
        Token.NOT: 2,
        Token.AND: 1,
        Token.OR: 1,
        Token.XOR: 1,
        Token.IMPL: 0,
        Token.EQ: 0
    }

    result = []
    operators = []

    for token in expr:
        if token == Token.PAREN_LEFT:
            operators.append(token)
        elif token == Token.PAREN_RIGHT:
            while operators[-1] != Token.PAREN_LEFT:
                result.append(operators.pop())
            operators.pop()
        elif token in [Token.NOT, Token.AND, Token.OR, Token.XOR, Token.IMPL, Token.EQ]:
            while len(operators) > 0 \
                    and operators[-1] != Token.PAREN_LEFT \
                    and priorities[operators[-1]] >= priorities[token]:
                result.append(operators.pop())

            operators.append(token)
        elif type(token) is VarToken or token in [Token.CONST_0, Token.CONST_1]:
            result.append(token)
        else:
            assert False

    while len(operators) > 0:
        result.append(operators.pop())

    return result


class Parser:

    def __init__(self, expr: str):
        self.expr = expr
        self.variables = None
        self.rpn = None

    def parse(self) -> bool:
        tokens = _tokenize(self.expr)

        if tokens is None:
            return False

        if not _validate(tokens):
            return False

        self.variables = _extract_variables(tokens)
        self.rpn = _infix_to_rpn(tokens)

        return True

    def get_variables(self) -> Tuple[str]:
        return tuple(self.variables)

    def get_rpn_expr(self) -> TokenList:
        return list(self.rpn)
