from typing import Iterable, Optional

from Minterm import Minterm

TriLogic = Optional[bool]


class Implicant:
    @staticmethod
    def from_minterm(minterm: Minterm):
        return Implicant(minterm.bits, [minterm])

    def __init__(self, bits: Iterable[TriLogic], minterms: Iterable[Minterm]):
        self.bits = tuple(bits)
        self.minterms = frozenset(minterms)

    def __str__(self):
        def bit_to_string(bit):
            if bit is True:
                return '1'
            elif bit is False:
                return '0'
            elif bit is None:
                return '-'

        minterm_decimals = sorted(minterm.decimal for minterm in self.minterms)

        return ' '.join(bit_to_string(bit) for bit in self.bits) + \
               '  m(' + ','.join(map(str, minterm_decimals)) + ')'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.bits == other.bits

    def __hash__(self):
        return self.bits.__hash__()

    def combine_with(self, other):
        conflicts = []  # '0' and '1' on same position
        self_contains_other = []  # self has '-', other has '0'/'1'
        other_contains_self = []  # self has '0'/'1', other has '-'

        for idx, (b1, b2) in enumerate(zip(self.bits, other.bits)):
            if b1 is not None and b2 is not None and b1 != b2:
                conflicts.append(idx)
            elif b1 is None and b2 is not None:
                self_contains_other.append(idx)
            elif b1 is not None and b2 is None:
                other_contains_self.append(idx)
            else:
                assert b1 == b2

        if not conflicts and self_contains_other and not other_contains_self:
            return Implicant(self.bits, self.minterms | other.minterms)
        elif not conflicts and not self_contains_other and other_contains_self:
            return Implicant(other.bits, self.minterms | other.minterms)
        elif len(conflicts) == 1 and not self_contains_other and not other_contains_self:
            bits = list(self.bits)
            bits[conflicts[0]] = None
            return Implicant(bits, self.minterms | other.minterms)
        else:
            return None

    def get_0_bits(self):
        return [idx for idx, bit in enumerate(self.bits) if bit is False]

    def get_1_bits(self):
        return [idx for idx, bit in enumerate(self.bits) if bit is True]
