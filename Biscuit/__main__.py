def main():
    # Whatever your execution code is
    from tkinter import Tk
    from .Windows import MainWindow

    import os
    from os.path import dirname
    os.chdir(dirname(__file__))

    root = Tk()

    m = MainWindow(master=root)
    m.mainloop()


if __name__ == "__main__":
    main()
