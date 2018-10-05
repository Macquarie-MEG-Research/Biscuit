from tkinter import StringVar, Tk
from contextlib import redirect_stdout
from time import time


class Holder(StringVar):
    def __init__(self, *args, **kwargs):
        super(Holder, self).__init__(*args, **kwargs)

    def write(self, value):
        if value != '\n':
            self.set(self.get() + value)

root = Tk()
a = Holder()
with redirect_stdout(a):
    print('hello lots of people')
