import itertools
from typing import List, Tuple

import Evaluator
from Implicant import Implicant
from Parser import TokenList


def generate_bit_lists(count: int) -> List[Tuple[bool]]:
    return list(itertools.product([False, True], repeat=count))


def generate_minterms(expr_rpn: TokenList, variables: Tuple[str, ...]) -> Tuple[List[int], List[Implicant]]:
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
