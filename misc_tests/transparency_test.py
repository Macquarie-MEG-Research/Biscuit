from tkinter import Tk, Frame, PhotoImage, Label
from tkinter import Button as tkButton
from tkinter.ttk import Style, Button
import time
from functools import wraps

from PIL import Image, ImageTk

from tkinter import StringVar
from contextlib import redirect_stdout

import re


def threaded(func):
    """
    Simple function to be used as a decorator to allow the
    decorated function to be threaded automatically
    """
    from threading import Thread

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class StreamedVar(StringVar):
    def __init__(self, pattern=None, *args, **kwargs):
        """
        pattern is a regex pattern which can be matched
        to only allow the value to be updated if there is a match.
        This allows filtering of output
        """

        super(StreamedVar, self).__init__(*args, **kwargs)
        self._curr_value = StringVar()
        if pattern is not None:
            self.pattern = re.compile(pattern)

    def write(self, value):
        if value != '\n':
            self.set(self.get() + value)
        else:
            if re.match(self.pattern, self.get()):
                self.curr_value.set(self.get())
                self.set('')
            else:
                self.set('')

    def get_curr(self):
        return self.curr_value.get()

    @property
    def curr_value(self):
        return self._curr_value


def RBGAImage(path):
    return Image.open(path).convert("RGBA")


class main(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.master = master

        self.a = StreamedVar('.*test.*')
        self.text_var = self.a.curr_value

        self.num = 1

        #icon = RBGAImage("biscuit.gif")
        self.icon = Image.open("assets/remove_row_trans.png")
        self.icon1 = self.icon.resize((51, 51), Image.LANCZOS)
        self.icon1 = ImageTk.PhotoImage(self.icon1)
        self.icon2 = self.icon.resize((51, 51))
        self.icon2 = ImageTk.PhotoImage(self.icon2)
        self.icon3 = self.icon.resize((51, 51), Image.HAMMING)
        self.icon3 = ImageTk.PhotoImage(self.icon3)
        self.icon4 = self.icon.resize((51, 51), Image.BICUBIC)
        self.icon4 = ImageTk.PhotoImage(self.icon4)
        #self.icon = PhotoImage(file="biscuit.png")
        #self.icon = self.icon.subsample(10)
        #self.delete_icon = ImageTk.PhotoImage(icon)

        Label(self.master, text="Click the biscuit ->").pack(side='left')

        self.btn1 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn1.config(image=self.icon1)
        self.btn1.pack(side='left')
        self.btn2 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn2.config(image=self.icon2)
        self.btn2.pack(side='left')
        self.btn3 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn3.config(image=self.icon3)
        self.btn3.pack(side='left')
        self.btn4 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn4.config(image=self.icon4)
        self.btn4.pack(side='left')

        self.changing_lbl = Label(self.master, textvariable=self.text_var)
        self.changing_lbl.pack()

        self.dostuff()

    @threaded
    def dostuff(self):
        print('doing stuff')
        with redirect_stdout(self.a):
            print('Initial test...')
            time.sleep(1)
            print("this shouldn't print")
            time.sleep(1)
            print('test will')
            time.sleep(1)
            print('maybe this test too???')
        print('no longer doing stuff')

    def printer(self):
        print(self.num)
        self.num += 1


if __name__ == "__main__":
    root = Tk()
    app = main(root)
    app.mainloop()
