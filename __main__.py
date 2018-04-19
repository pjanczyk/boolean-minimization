import MintermFinder
from FinalResultFormatter import FinalResultFormatter
from Parser import Parser
from PrimeImplicantChart import PrimeImplicantChart
from PrimeImplicantsFinder import PrimeImplicantsFinder


def main():
    # expr = sys.argv[1]
    # expr = '(A | B) & (A | C) => (B ^ C)'
    expr = '(!A & B & !C & !D) | ' \
           '(A & !B & !C & !D) | ' \
           '(A & !B & C & !D) | ' \
           '(A & !B & C & D) | ' \
           '(A & B & !C & !D) | ' \
           '(A & B & C & D)'
    # expr = 'A & 0'

    parser = Parser(expr)
    if not parser.parse():
        print("Error: Invalid input")
        return

    variables = parser.get_variables()
    rpn = parser.get_rpn_expr()

    print("Variables:", ', '.join(variables))
    print("RPN:", ' '.join(map(str, rpn)))

    minterms, implicants = MintermFinder.generate_minterms(rpn, variables)

    prime_implicants = PrimeImplicantsFinder(implicants, debug_log=True).find_prime_implicants()

    result = PrimeImplicantChart(minterms, prime_implicants).run()

    # for result in results:
    simplified_expr = FinalResultFormatter(variables, result).format()
    print("Final result:")
    print(simplified_expr)


if __name__ == '__main__':
    main()
