import inspect

# Ported from https://github.com/dirigeants/klasa/blob/master/src/lib/util/Type.js
# Works pretty fine and has better function argument typings
# but circular checking is currently broken
# not like we will meet circulars that much
class Type:
    def __init__(self, value, parent = None):
        self.value = value
        self._is = self.__class__.resolve(value)
        self.parent = parent
        self.child_keys = {}
        self.child_values = {}
        self._frozen = False

    @property
    def child_types(self):
        if not len(self.child_values):
            return ""
        return "<" + (f"{self.__class__.list(self.child_keys)}, " if len(self.child_keys) else "") + self.__class__.list(self.child_values) + ">"

    def __str__(self):
        self.check()
        return self._is + self.child_types

    def add_value(self, value):
        child = self.__class__(value, self)
        self.child_values[child._is] = child

    def add_entry(self, key, value):
        child = self.__class__(key, self)
        self.child_keys[child._is] = child
        self.add_value(value)

    def parents(self):
        current = self
        while current:
            current = current.parent
            if not current:
                continue
            yield current

    def check(self):
        if self._frozen:
            return
        if isinstance(self.value, object) and self.is_circular():
            self._is = f"[Circular:{self._is}]"
        elif isinstance(self.value, dict):
            for key, value in self.value.items():
                self.add_entry(key, value)
        elif isinstance(self.value, list) or isinstance(self.value, set) or isinstance(self.value, tuple):
            for value in self.value:
                self.add_value(value)
        elif self._is == "object":
            self._is = "any"
        self._frozen = True


    def is_circular(self):
        parents = self.parents()
        if parents is None:
            return False
        for parent in parents:
            if parent.value == self.value:
                return True
        return False

    @staticmethod
    def resolve(value):
        t = type(value).__name__
        if t == "NoneType":
            return "void"
        if t == "function" or t == "method":
            return f"{value.__name__}{inspect.formatargspec(*inspect.getfullargspec(value))}"
        return t

    @staticmethod
    def list(values):
        if "any" in values:
            return "any"
        vals = list(map(lambda x: str(x), values))
        return " | ".join(sorted(vals))
