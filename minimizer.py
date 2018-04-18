import string
import sys
from enum import Enum
import itertools
from typing import List, Union


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

        if expr[i] in string.ascii_letters:
            begin = i

            while i < len(expr) and expr[i] in string.ascii_letters:
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
    return sorted(set(token.name for token in tokens if type(token) is VarToken))


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
            raise AssertionError()

    if len(stack) != 1:
        raise AssertionError()

    return stack.pop()


class Minterm:
    def __init__(self, bits, sources=None):
        self.bits = tuple(bits)
        if sources:
            self.sources = set(sources)
        else:
            number = sum(2 ** idx for idx, bit in enumerate(bits) if bit)
            self.sources = {number}

    def __str__(self):
        def bit_to_string(bit):
            if bit is True:
                return '1'
            elif bit is False:
                return '0'
            elif bit is None:
                return '-'

        return ' '.join(bit_to_string(bit) for bit in self.bits) + \
               '  m(' + ','.join(map(str, sorted(self.sources))) + ')'

    def __eq__(self, other):
        return self.bits == other.bits

    def __hash__(self):
        return self.bits.__hash__()

    def combine_with(self, other):
        conflicts = []  # '0' and '1' on same position
        self_contains_other = []  # self has '-', other has '0'/'1'
        other_contains_self = []  # self has '0'/'1', other has '-'

        for idx, (b1, b2) in enumerate(zip(self.bits, other.bits)):
            if b1 is not None and b2 is not None and b1 != b2:
                conflicts.append(idx)
            elif b1 is None and b2 is not None:
                self_contains_other.append(idx)
            elif b1 is not None and b2 is None:
                other_contains_self.append(idx)
            else:
                assert b1 == b2

        if not conflicts and self_contains_other and not other_contains_self:
            return Minterm(self.bits, self.sources | other.sources)
        elif not conflicts and not self_contains_other and other_contains_self:
            return Minterm(other.bits, self.sources | other.sources)
        elif len(conflicts) == 1 and not self_contains_other and not other_contains_self:
            bits = list(self.bits)
            bits[conflicts[0]] = None
            return Minterm(bits, self.sources | other.sources)
        else:
            return None


class MintermCombiner:
    def __init__(self, minterms, debug_log=False):
        self.minterms = list(minterms)
        self.debug_log = debug_log

    def run(self):
        self.debug_print("Original:")

        while True:
            n = len(self.minterms)

            any_combined = self.phase_combine()
            self.debug_print("Combined:")

            self.phase_remove_duplicates()
            self.debug_print("Removed duplicates:")

            if not any_combined:
                break

    def phase_combine(self):
        any_combined = False
        used = [False] * len(self.minterms)

        results = []

        for (idx1, minterm1), (idx2, minterm2) in (itertools.combinations(enumerate(self.minterms), 2)):
            combined = minterm1.combine_with(minterm2)

            if combined is not None:
                used[idx1] = True
                used[idx2] = True
                results.append(combined)
                any_combined = True

        results += [minterm for idx, minterm in enumerate(self.minterms) if not used[idx]]

        self.minterms = results

        return any_combined

    def phase_remove_duplicates(self):
        self.minterms = list(set(self.minterms))

    def debug_print(self, msg):
        if self.debug_log:
            print(msg)
            for minterm in self.minterms:
                print(str(minterm))
            print()


class PrimeImplicantChart:

    def __init__(self, original_minterms, combined_minterms):
        self.original_minterms = sorted(next(iter(minterm.sources)) for minterm in original_minterms)
        self.combined_minterms = combined_minterms

    def run(self):
        used_original = set()
        used_combined = set()

        for minterm in self.original_minterms:
            if minterm in used_original:
                continue

            related_combined = [combined for combined in self.combined_minterms
                                if combined not in used_combined and minterm in combined.sources]

            if len(related_combined) == 1:
                used_original |= related_combined[0].sources
                used_combined.add(related_combined[0])

        for combined in self.combined_minterms:
            for original in self.original_minterms:
                if original in combined.sources:
                    print('X ', end='')
                else:
                    print('O ', end='')
            print(combined)

        return used_combined


def main():
    # expr = sys.argv[1]
    expr = '(A | B) & (A | C)'
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
            minterms.append(Minterm(v))

    mc = MintermCombiner(minterms, debug_log=True)
    mc.run()
    combined_minterms = mc.minterms

    pic = PrimeImplicantChart(minterms, combined_minterms)

    result = pic.run()

    print("Final result:")
    for minterm in result:
        print(str(minterm))
    print()


if __name__ == '__main__':
    main()
