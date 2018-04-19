from typing import Dict, List

from Parser import Token, Tokens, VarToken


def evaluate(rpn: List[Token], variable_values: Dict[str, bool]) -> bool:
    stack = []

    unary_operators = {
        Tokens.NOT: lambda a: not a
    }

    binary_operators = {
        Tokens.AND: lambda a, b: a and b,
        Tokens.OR: lambda a, b: a or b,
        Tokens.XOR: lambda a, b: a != b,
        Tokens.EQ: lambda a, b: a == b,
        Tokens.IMPL: lambda a, b: not a or b
    }

    for token in rpn:
        if type(token) is VarToken:
            # noinspection PyUnresolvedReferences
            stack.append(variable_values[token.name])
        elif token == Tokens.CONST_0:
            stack.append(False)
        elif token == Tokens.CONST_1:
            stack.append(True)
        elif token in unary_operators.keys():
            obj = stack.pop()
            val = unary_operators[token](obj)
            stack.append(val)
        elif token in binary_operators.keys():
            rhs = stack.pop()
            lhs = stack.pop()
            val = binary_operators[token](lhs, rhs)
            stack.append(val)
        else:
            assert False

    assert len(stack) == 1

    return stack.pop()
