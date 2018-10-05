from tkinter import StringVar, Tk
from contextlib import redirect_stdout


# TODO: make this really cool!
class Holder(StringVar):
    def __init__(self, *args, **kwargs):
        super(Holder, self).__init__(*args, **kwargs)
        self._curr_value = StringVar()

    def write(self, value):
        if value != '\n':
            self.set(self.get() + value)
        else:
            self.curr_value.set(self.get())
            self.set('')

    def get_curr(self):
        return self.curr_value.get()

    @property
    def curr_value(self):
        return self._curr_value



root = Tk()
a = Holder()
with redirect_stdout(a):
    print('hello lots of people')
    print('well now')
    print('this *is* interesting')
    print('...ok... maybe not')

print(a.get())
