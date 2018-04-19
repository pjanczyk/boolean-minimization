import itertools
from typing import Iterable

from Implicant import Implicant
from Minterm import Minterm


class PrimeImplicantsFinder:
    def __init__(self, minterms: Iterable[Minterm], debug_log=False):
        self.implicants = [Implicant.from_minterm(minterm) for minterm in minterms]
        self.debug_log = debug_log

    def find_prime_implicants(self):
        if self.debug_log:
            print()
            print("Finding prime implicants:")

        self._debug_print("Initial::")

        while True:
            any_combined = self._phase_combine()
            self._debug_print("Combined:")

            self._phase_remove_duplicates()
            self._debug_print("Removed duplicates:")

            if not any_combined:
                break

        return self.implicants

    def _phase_combine(self):
        any_combined = False
        used = [False] * len(self.implicants)

        results = []

        for (idx1, implicant1), (idx2, implicant2) in itertools.combinations(enumerate(self.implicants), 2):
            combined = implicant1.combine_with(implicant2)

            if combined is not None:
                used[idx1] = True
                used[idx2] = True
                results.append(combined)
                any_combined = True

        results += [minterm for idx, minterm in enumerate(self.implicants) if not used[idx]]

        self.implicants = results

        return any_combined

    def _phase_remove_duplicates(self):
        self.implicants = list(set(self.implicants))

    def _debug_print(self, msg):
        if self.debug_log:
            print(msg)
            for implicant in self.implicants:
                print(str(implicant))
            print()
