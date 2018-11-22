import pytest

#from Biscuit.Management import ClickContext
from Management import ClickContext
from Management.CustomVars import StreamedVar, OptionsVar


def test_ClickContext():
    a = ClickContext()
    a.set('foo')
    assert a.get() == 'hi'
    a.set('bar')
    assert a.get() == 'bar'
    assert a.changed
    a.set(['foo', 'bar'])
    assert a.is_mixed
    a.set(['foo', 'foo', 'foo'])
    assert a.group_size == 3
    assert not a.is_mixed


def test_StreamedVar():
    from tkinter import Tk
    Tk()

    s = StreamedVar()


def test_OptionsVar():
    from tkinter import Tk
    Tk()

    m = OptionsVar(options=['foo', 'bar'])
    assert m.options == ['foo', 'bar']
    m.set('foo')
    assert m.get() == 'foo'
    assert len(m) == 2
    with pytest.raises(ValueError):
        m.set('spam')
