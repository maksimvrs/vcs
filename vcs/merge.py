class MergeUnitStatus:
    Stable = 0
    Conflict = 1


class MergeUnit:
    def __init__(self, original, first, second, status):
        self._original = original
        self._first = first
        self._second = second
        self._status = status

    @property
    def original(self):
        return self._original

    @property
    def first(self):
        return self._first

    @property
    def second(self):
        return self._second

    @property
    def status(self):
        return self._status


class Merge:
    def __init__(self):
        self.units = list()
        self.index = 0

    def add(self, merge_unit):
        self.units.append(merge_unit)

    def add_right(self, merge):
        self.units[len(self.units):len(self.units)] = merge

    def add_left(self, merge):
        self.units[0:0] = merge

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.units):
            result = self.units[self.index]
            self.index += 1
        else:
            raise StopIteration
        return result
