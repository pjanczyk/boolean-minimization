from typing import Tuple


class Minterm:
    def __init__(self, bits: Tuple[bool]):
        self.bits = bits
        self.decimal = sum(2 ** idx for idx, bit in enumerate(bits) if bit)

    def __eq__(self, other):
        return self.decimal == other.decimal

    def __hash__(self):
        return self.decimal.__hash__()
