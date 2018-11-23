def main():
    # main entry point to run the Biscuit GUI
    from tkinter import Tk
    import os
    from os.path import dirname
    os.chdir(dirname(__file__))

    from .Windows import MainWindow

    root = Tk()

    m = MainWindow(master=root)
    m.mainloop()


if __name__ == "__main__":
    main()
