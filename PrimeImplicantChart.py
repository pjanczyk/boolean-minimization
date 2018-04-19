from typing import Iterable, List

import MintermFinder
from Implicant import Implicant
from Minterm import Minterm
from Parser import VarToken, Tokens
from PrimeImplicantsFinder import PrimeImplicantsFinder


class PrimeImplicantChart:

    def __init__(self, minterms: Iterable[Minterm], prime_implicants: Iterable[Implicant], debug: bool = False):
        self.minterms = tuple(minterms)
        self.prime_implicants = tuple(prime_implicants)
        self.debug = debug

        self.used_minterms = set()
        self.used_implicants = set()

    def run(self) -> List[Implicant]:
        if self.debug:
            print("Prime implicant chart:")
            print("Initial:")
            self._debug_print()

        while self._eliminate_essential_prime_implicants():

            if self.debug:
                print("Eliminated essential prime implicants:")
                self._debug_print()

        if len(self.used_minterms) == len(self.minterms):
            return list(self.used_implicants)
        else:
            if self.debug:
                print("Using Patrick's method:")
            return self._patricks_method()

    def _debug_print(self):
        print('     ', end='')
        for minterm in self.minterms:
            if minterm in self.used_minterms:
                continue
            print(f'm{minterm.decimal}'.center(5), end='')
        print()

        for implicant_idx, implicant in enumerate(self.prime_implicants):
            if implicant in self.used_implicants:
                continue

            print(f'${implicant_idx} | ', end='')

            for minterm in self.minterms:
                if minterm in self.used_minterms:
                    continue

                if minterm in implicant.minterms:
                    print('X'.center(5), end='')
                else:
                    print('.'.center(5), end='')

            print(' | ', end='')
            print(implicant)
        print()

    def _eliminate_essential_prime_implicants(self) -> bool:
        any_eliminated = False

        for minterm in self.minterms:
            if minterm in self.used_minterms:
                continue

            related_implicants = [implicant for implicant in self.prime_implicants
                                  if implicant not in self.used_implicants and minterm in implicant.minterms]

            if len(related_implicants) == 1:
                self.used_minterms |= related_implicants[0].minterms
                self.used_implicants.add(related_implicants[0])
                any_eliminated = True

        return any_eliminated

    def _patricks_method(self):
        sum_of_products = []

        not_used_minterms = [minterm for minterm in self.minterms if minterm not in self.used_minterms]

        for minterm in not_used_minterms:
            related_implicant_indices = [idx for idx, implicant in enumerate(self.prime_implicants)
                                         if implicant not in self.used_implicants and minterm in implicant.minterms]

            sum_of_products += [VarToken(idx) for idx in related_implicant_indices]
            sum_of_products += [Tokens.AND] * (len(related_implicant_indices) - 1)

        sum_of_products += [Tokens.OR] * (len(not_used_minterms) - 1)

        if self.debug:
            print("RPN:", ' '.join(map(str, sum_of_products)))

        variables = tuple(idx for idx, implicant in enumerate(self.prime_implicants)
                          if implicant not in self.used_implicants)

        minterms = MintermFinder.find_minterms(sum_of_products, variables)
        prime_implicants = PrimeImplicantsFinder(minterms, debug_log=self.debug).find_prime_implicants()

        terms = [implicant.get_1_bits() for implicant in prime_implicants]

        shortest_len = min(len(term) for term in terms)

        terms = [term for term in terms if len(term) == shortest_len]
        terms = [[self.prime_implicants[variables[idx]] for idx in term] for term in terms]

        def count_literals(term):
            return sum(len(implicant.get_0_bits()) + len(implicant.get_1_bits()) for implicant in term)

        return min(terms, key=count_literals)
