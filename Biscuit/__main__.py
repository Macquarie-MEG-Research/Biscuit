def main():
    # Whatever your execution code is
    from tkinter import Tk
    import os
    from os.path import dirname
    os.chdir(dirname(__file__))

    if __name__ == "__main__":
        from Windows import MainWindow
    else:
        from .Windows import MainWindow

    root = Tk()

    m = MainWindow(master=root)
    m.mainloop()


if __name__ == "__main__":
    main()
