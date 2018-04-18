import string
import sys
from enum import Enum
import itertools


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

    def __repr__(self):
        return self.value


class VarToken:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '$' + self.name


def tokenize(expr):
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

        if expr[i] in string.ascii_lowercase:
            begin = i

            while i < len(expr) and expr[i] in string.ascii_lowercase:
                i += 1

            text = expr[begin:i]
            results.append(VarToken(text))
            continue

        return False

    return results


def validate(tokens):
    state = 1
    parentheses = 0

    for token in tokens:
        if state == 1:
            if token == Token.PAREN_LEFT:
                parentheses += 1
            elif token == Token.NOT:
                pass
            elif type(token) is VarToken:
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


def extract_variables(tokens):
    return sorted(token.name for token in tokens if type(token) is VarToken)


def generate_values(count):
    return list(itertools.product([False, True], repeat=count))


def infix_to_rpn(tokens):
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

    for token in tokens:
        if token == Token.PAREN_LEFT:
            operators.append(token)
        elif token == Token.PAREN_RIGHT:
            while operators[-1] != Token.PAREN_LEFT:
                result.append(operators.pop())
            operators.pop()
        elif token in [Token.NOT, Token.AND, Token.OR, Token.XOR, Token.IMPL, Token.EQ]:
            while len(operators) > 0 \
                    and operators[-1] != Token.PAREN_LEFT \
                    and priorities[operators[-1]] > priorities[token]:
                result.append(operators.pop())

            operators.append(token)
        elif type(token) is VarToken:
            result.append(token)

    while len(operators) > 0:
        result.append(operators.pop())

    return result


def evaluate(rpn, variable_values):
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
            stack.append(lhs and rhs)
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
            raise AssertionError()

    if len(stack) != 1:
        raise AssertionError()

    return stack.pop()


def print_minterms(minterms):
    def bit_to_string(bit):
        if bit is True:
            return '1'
        elif bit is False:
            return '0'
        elif bit is None:
            return '-'

    print()
    for minterm in minterms:
        print(' '.join(map(bit_to_string, minterm)))
    print()


def combine_minterms(minterms):
    def combine(minterm1, minterm2):
        diff = []
        for idx, (v1, v2) in enumerate(zip(minterm1, minterm2)):
            if v1 is not None and v2 is not None and v1 != v2:
                diff.append(idx)

        if len(diff) != 1:
            return None
        else:
            combined = list(minterm1)
            combined[diff[0]] = None
            return tuple(combined)

    used = [False] * len(minterms)

    results = []

    for (idx1, minterm1), (idx2, minterm2) in (itertools.combinations(enumerate(minterms), 2)):
        combined = combine(minterm1, minterm2)

        if combined is not None:
            used[idx1] = True
            used[idx2] = True
            results.append(combined)

    results += [minterm for idx, minterm in enumerate(minterms) if not used[idx]]

    return results


def main():
    # expr = sys.argv[1]
    expr = 'a & !b == (b => c)'
    tokens = tokenize(expr)

    if tokens is False:
        print("Error: Invalid input")
        return

    print("Tokens:", tokens)

    if not validate(tokens):
        print("Error: Invalid input")
        return

    variables = extract_variables(tokens)
    rpn = infix_to_rpn(tokens)

    print("Variables:", variables)
    print("RPN:", rpn)

    values = generate_values(len(variables))
    print(values)

    minterms = []

    for v in values:
        variable_dict = dict(zip(variables, v))
        evaluated = evaluate(rpn, variable_dict)
        print(v, evaluated)
        if evaluated:
            minterms.append(tuple(v))

    for _ in range(3):
        minterms = combine_minterms(minterms)
        print_minterms(minterms)


if __name__ == '__main__':
    main()
