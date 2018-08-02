from tkinter import StringVar


class Dummy():
    """
    This is an empty class that will simply return a tkinter StringVar
    no matter what property is called on it.
    This is used to be set as a default info container (etc) so that many gui
    elements can be drawn before any data is actually assigned to them.
    """
    def __init__(self):
        pass

    def __getattr__(self, name):
        if name == 'check_bids_ready':
            return lambda: False
        else:
            s = StringVar(value='')
            return ('dummy', s)


if __name__ == "__main__":
    from tkinter import Tk
    Tk()
    d = Dummy()
    a = d.test
    a.set('wow!')
    print(a.get())
    b = d.somethingstupid
    print(b.get(), 'alt')
