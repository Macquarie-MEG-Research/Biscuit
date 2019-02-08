__version__ = '0.9.7'
name = "Biscuit"  # noqa


def run():
    # main entry point to run the Biscuit GUI
    from tkinter import Tk
    import os
    from os.path import dirname
    os.chdir(dirname(__file__))

    from .Windows import MainWindow

    root = Tk()

    m = MainWindow(master=root)
    m.mainloop()
