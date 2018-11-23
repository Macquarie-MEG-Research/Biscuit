# script to allow for testing of Biscuit without having to build a wheel

import Biscuit
from Biscuit.Windows.MainWindow import MainWindow
from tkinter import Tk

import os
from os.path import dirname
os.chdir(dirname(Biscuit.__file__))

root = Tk()
m = MainWindow(master=root)
m.mainloop()
