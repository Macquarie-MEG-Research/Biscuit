"""
A singleton class to keep track of the click context.
This will store the currently clicked context as well as the previous context.
"""


class ClickContext():
    __instance = None

    def __new__(cls, *val):
        """ Singleton implementation """
        if ClickContext.__instance is None:
            ClickContext.__instance = object.__new__(cls)
        ClickContext.__instance.val = val
        return ClickContext.__instance

    def __init__(self):
        # both the states are stored as sets
        self._previous = set()
        self._current = set()
        self.group_size = 1
        self.is_mixed = False

    def __contains__(self, item):
        """ Returns True if the item is in the current context """
        try:
            return item in self._current
        except TypeError:
            # in this case self._current isn't an iterable
            return False

    def add(self, other):
        """
        Add another click context to the current context.
        This will automatically detect whether the context is a "GROUP"
        or "MIXED" context.
        """

        self._previous = self._current.copy()
        if isinstance(other, set):
            # not sure what to do here...
            self._current.update(other)
        else:
            if other in self._current:
                self._current.add('GROUP')
            else:
                if len(self._current) != 0:
                    self._current = {'MIXED'}
                else:
                    self._current = {other}

    def __eq__(self, other):
        """
        Returns True if other is equal to the current click context.
        This will be a strict comparison and will return False if either
        self.is_mixed or self.group_size != 1.
        Returns False otherwise.
        """
        if not isinstance(other, set):
            other = {other}
        return ((self._current == other) and
                (self.is_mixed is False) and
                (self.group_size == 1))

    # have get and set methods like tkinter variables

    def set(self, value=set()):
        """ set the current value as value
        and set the previous value """
        self._previous = self._current
        self.group_size = 1
        self.is_mixed = False
        if isinstance(value, set):
            if len(value) > 1:
                self._current = value
                self.is_mixed = True
            else:
                self._current = value
                self.is_mixed = False
        elif isinstance(value, list):
            keys = set(value)
            self._current = keys
            if len(keys) == 1:
                self.group_size = len(value)
            else:
                self.is_mixed = True
        else:
            self._current = {value}

    def get(self):
        """ Returns the current context """
        return self._current

    @property
    def current(self):
        """ Returns the current context """
        return self._current

    @property
    def previous(self):
        return self._previous

    @property
    def changed(self):
        """
        Returns True if the context has changed.
        Returns False if it has remained the same.
        This will not be capable of detecting whether or not the number of
        entries has changed (for example).
        """
        return self._previous != self._current

    def __str__(self):
        return 'Current value: {0}\nPrevious value: {1}'.format(self._current,
                                                                self._previous)


if __name__ == "__main__":
    a = ClickContext()
    a.set("hi")
    print(a.get())
    a.set("there")
    print(a.get())
    a.set(['what', 's'])
    print(a.get())
    print(a.is_mixed)
    a.set(['hi', 'hi', 'hi'])
    print(a.get())
    print(a.group_size)
    print(a.is_mixed)
    print(a == 'hi')
    a.set('hi')
    print(a)
    print(a == 'hi')
