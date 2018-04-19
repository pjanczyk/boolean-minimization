import sys

import MintermFinder
from FinalResultFormatter import FinalResultFormatter
from Parser import Parser
from PrimeImplicantChart import PrimeImplicantChart
from PrimeImplicantsFinder import PrimeImplicantsFinder


def simplify(expr: str, debug_log=False):
    parser = Parser(expr, debug_log)
    if not parser.parse():
        print("Error: Invalid input")
        return

    variables = parser.get_variables()
    rpn = parser.get_rpn_expr()

    minterms = MintermFinder.find_minterms(rpn, variables)

    prime_implicants = PrimeImplicantsFinder(minterms, debug_log).find_prime_implicants()

    result = PrimeImplicantChart(minterms, prime_implicants, debug_log).run()

    simplified_expr = FinalResultFormatter(variables, result).format()

    if debug_log:
        print()
        print("Final result:")

    print(simplified_expr)


def main():
    # simplify('(!A & B & !C & !D) | (A & !B & !C & !D) | (A & !B & C & !D) | (A & !B & C & D) | (A & B & !C & !D) | (A & B & C & D)', False)
    debug = True

    if len(sys.argv) == 2:
        expr = sys.argv[1]
        simplify(expr, debug_log=debug)
        return

    try:
        while True:
            print()
            expr = input("Expr: ")
            simplify(expr, debug_log=debug)
    except EOFError:
        print()
        pass


if __name__ == '__main__':
    main()
