import itertools
from typing import List, Tuple

import Evaluator
from FinalResultFormatter import FinalResultFormatter
from Implicant import Implicant
from Parser import Parser, TokenList
from PrimeImplicantChart import PrimeImplicantChart
from PrimeImplicantsFinder import PrimeImplicantsFinder


def generate_bit_lists(count: int) -> List[Tuple[bool]]:
    return list(itertools.product([False, True], repeat=count))


def generate_minterms(expr_rpn: TokenList, variables: Tuple[str]) -> Tuple[List[int], List[Implicant]]:
    minterms: List[int] = []
    implicants: List[Implicant] = []

    values = generate_bit_lists(len(variables))

    for value in values:
        variable_values = dict(zip(variables, value))
        evaluated_value = Evaluator.evaluate(expr_rpn, variable_values)

        if evaluated_value:
            implicant = Implicant(value)
            minterm = next(iter(implicant.minterms))

            implicants.append(implicant)
            minterms.append(minterm)

    return minterms, implicants


def main():
    # expr = sys.argv[1]
    expr = '(A | B) & (A | C) => (B ^ C)'
    # expr = 'A & 0'

    parser = Parser(expr)
    if not parser.parse():
        print("Error: Invalid input")
        return

    variables = parser.get_variables()
    rpn = parser.get_rpn_expr()

    print("Variables:", ', '.join(variables))
    print("RPN:", ' '.join(map(str, rpn)))

    minterms, implicants = generate_minterms(rpn, variables)

    prime_implicants = PrimeImplicantsFinder(implicants, debug_log=True).find_prime_implicants()

    result = PrimeImplicantChart(minterms, prime_implicants).run()

    simplified_expr = FinalResultFormatter(variables, result).format()
    print("Final result:")
    print(simplified_expr)


if __name__ == '__main__':
    main()
