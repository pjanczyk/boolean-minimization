import itertools
from typing import List, Tuple

import Evaluator
from Minterm import Minterm
from Parser import Token


def _generate_bit_sequences(count: int) -> List[Tuple[bool]]:
    return list(itertools.product([False, True], repeat=count))


def find_minterms(expr_rpn: List[Token], variables: List[str]) -> List[Minterm]:
    minterms = []

    values = _generate_bit_sequences(len(variables))

    for value in values:
        variable_values = dict(zip(variables, value))
        evaluated_value = Evaluator.evaluate(expr_rpn, variable_values)

        if evaluated_value:
            minterms.append(Minterm(value))

    return list(sorted(minterms, key=lambda minterm: minterm.decimal))
