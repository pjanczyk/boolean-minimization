from typing import Iterable

from Implicant import Implicant


class FinalResultFormatter:

    def __init__(self, variables: Iterable[str], implicants: Iterable[Implicant]):
        self.variables = tuple(variables)
        self.implicants = tuple(implicants)

    def format(self) -> str:
        if self.implicants:
            return ' | '.join(map(self._format_implicant, self.implicants))
        else:
            return '0'

    def _format_implicant(self, implicant) -> str:
        terms = []
        for idx in implicant.get_0_bits():
            terms.append('!' + self.variables[idx])
        for idx in implicant.get_1_bits():
            terms.append(self.variables[idx])

        if len(terms) == 1:
            return terms[0]
        else:
            return '(' + ' & '.join(terms) + ')'
