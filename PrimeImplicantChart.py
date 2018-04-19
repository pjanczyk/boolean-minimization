from typing import Iterable

from Implicant import Implicant


class PrimeImplicantChart:

    def __init__(self, minterms: Iterable[int], prime_implicants: Iterable[Implicant]):
        self.minterms = tuple(minterms)
        self.prime_implicants = tuple(prime_implicants)

        self.used_minterms = set()
        self.used_implicants = set()

    def debug_print(self):
        for implicant in self.prime_implicants:
            for minterm in self.minterms:
                if minterm in implicant.minterms:
                    print('X ', end='')
                else:
                    print('. ', end='')
            print(implicant)

    def run(self):
        for minterm in self.minterms:
            if minterm in self.used_minterms:
                continue

            related_implicants = [implicant for implicant in self.prime_implicants
                                  if implicant not in self.used_implicants and minterm in implicant.minterms]

            if len(related_implicants) == 1:
                self.used_minterms |= related_implicants[0].minterms
                self.used_implicants.add(related_implicants[0])

        self.debug_print()
        return self.used_implicants
