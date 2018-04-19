from typing import Iterable

from Implicant import Implicant


class FinalResultFormatter:

    def __init__(self, variables: Iterable[str], implicants: Iterable[Implicant]):
        self.variables = tuple(variables)
        self.implicants = tuple(implicants)

    def format_implicant(self, implicant) -> str:
        terms = []
        for idx, bit in enumerate(implicant.bits):
            if bit is True:
                terms.append(self.variables[idx])
            elif bit is False:
                terms.append('!' + self.variables[idx])

        if len(terms) == 1:
            return terms[0]
        else:
            return '(' + ' & '.join(terms) + ')'

    def format(self) -> str:
        if self.implicants:
            return ' | '.join(map(self.format_implicant, self.implicants))
        else:
            return '0'
