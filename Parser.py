import string
from typing import List, Optional, Tuple


class Token:
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return str(self)


class Tokens:
    AND = Token('&')
    OR = Token('|')
    XOR = Token('^')
    NOT = Token('!')
    IMPL = Token('=>')
    EQ = Token('==')
    CONST_0 = Token('0')
    CONST_1 = Token('1')
    PAREN_LEFT = Token('(')
    PAREN_RIGHT = Token(')')

    ALL_TOKENS = [AND, OR, XOR, NOT, IMPL, EQ, CONST_0, CONST_1, PAREN_LEFT, PAREN_RIGHT]


class VarToken(Token):
    def __init__(self, name):
        super().__init__('$')
        self.name = name

    def __str__(self):
        return f'${self.name}'

    def __repr__(self):
        return str(self)


TokenList = List[Token]


def _tokenize(expr: str) -> Optional[TokenList]:
    results = []

    i = 0
    while i < len(expr):
        if expr[i] == ' ':
            i += 1
            continue

        matched = False
        for token in Tokens.ALL_TOKENS:
            symbol = token.symbol
            if i + len(symbol) <= len(expr) and symbol == expr[i:i + len(symbol)]:
                i += len(symbol)
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
            if token == Tokens.PAREN_LEFT:
                parentheses += 1
            elif token == Tokens.NOT:
                pass
            elif type(token) is VarToken or token in [Tokens.CONST_0, Tokens.CONST_1]:
                state = 2
            else:
                return False
        else:
            if token == Tokens.PAREN_RIGHT:
                parentheses -= 1
                if parentheses < 0:
                    return False
            elif token in [Tokens.AND, Tokens.OR, Tokens.XOR, Tokens.IMPL, Tokens.EQ]:
                state = 1
            else:
                return False

    return state == 2 and parentheses == 0


def _extract_variables(expr: TokenList) -> List[str]:
    return sorted(set(token.name for token in expr if type(token) is VarToken))


def _infix_to_rpn(expr: TokenList) -> TokenList:
    priorities = {
        Tokens.NOT: 2,
        Tokens.AND: 1,
        Tokens.OR: 1,
        Tokens.XOR: 1,
        Tokens.IMPL: 0,
        Tokens.EQ: 0
    }

    result = []
    operators = []

    for token in expr:
        if token == Tokens.PAREN_LEFT:
            operators.append(token)
        elif token == Tokens.PAREN_RIGHT:
            while operators[-1] != Tokens.PAREN_LEFT:
                result.append(operators.pop())
            operators.pop()
        elif token in [Tokens.NOT, Tokens.AND, Tokens.OR, Tokens.XOR, Tokens.IMPL, Tokens.EQ]:
            while len(operators) > 0 \
                    and operators[-1] != Tokens.PAREN_LEFT \
                    and priorities[operators[-1]] >= priorities[token]:
                result.append(operators.pop())

            operators.append(token)
        elif type(token) is VarToken or token in [Tokens.CONST_0, Tokens.CONST_1]:
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
