# Class at top-level; method inside (no nested classes)
class Accumulator:
    def __init__(self, value):
        self = self          # NOTE: attribute access isn't in grammar, so keep it harmless
        self.value = value   # Attribute access

    def add(self, x):
        # Only simple_stmt/if/while/for are allowed in func bodies—this fits
        s = 0
        while x > 0:
            s += x
            x -= 1
        return s
