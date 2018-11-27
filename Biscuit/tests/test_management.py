import pytest

from Biscuit.Management import ClickContext
from Biscuit.Management.CustomVars import StreamedVar, OptionsVar, RangeVar

# TODO: actually make these work...


def test_ClickContext():
    a = ClickContext()
    a.set('foo')
    assert a.get() == {'foo'}
    assert 'foo' in a
    a.set('bar')
    assert a == 'bar'
    assert a.changed
    a.set(['foo', 'bar'])
    assert a.is_mixed
    a.set(['foo', 'foo', 'foo'])
    assert a.group_size == 3
    assert not a.is_mixed


def test_StreamedVar():
    if __name__ == "__main__":
        from tkinter import Tk
        Tk()

        s = StreamedVar()


def test_OptionsVar():
    if __name__ == "__main__":
        from tkinter import Tk
        Tk()

        m = OptionsVar(options=['foo', 'bar'])
        assert m.options == ['foo', 'bar']
        m.set('foo')
        assert m.get() == 'foo'
        assert len(m) == 2
        with pytest.raises(ValueError):
            m.set('spam')


def test_RangeVar():
    if __name__ == "__main__":
        from tkinter import Tk
        Tk()

        a = RangeVar(max_val=100)
        a.set(10)
        print(a.get())
        print(a.max)
        a.max = 200
        print(a.max)