from typing import Dict

from Parser import VarToken, Token, TokenList


def evaluate(rpn: TokenList, variable_values: Dict[str, bool]) -> bool:
    stack = []

    for e in rpn:
        if type(e) is VarToken:
            stack.append(variable_values[e.name])
        elif e == Token.CONST_0:
            stack.append(False)
        elif e == Token.CONST_1:
            stack.append(True)
        elif e == Token.NOT:
            stack.append(not stack.pop())
        elif e == Token.AND:
            rhs = stack.pop()
            lhs = stack.pop()
            stack.append(lhs and rhs)
        elif e == Token.OR:
            rhs = stack.pop()
            lhs = stack.pop()
            stack.append(lhs or rhs)
        elif e == Token.XOR:
            rhs = stack.pop()
            lhs = stack.pop()
            stack.append(lhs != rhs)
        elif e == Token.EQ:
            rhs = stack.pop()
            lhs = stack.pop()
            stack.append(lhs == rhs)
        elif e == Token.IMPL:
            rhs = stack.pop()
            lhs = stack.pop()
            stack.append(not lhs or rhs)
        else:
            assert False

    assert len(stack) == 1

    return stack.pop()
