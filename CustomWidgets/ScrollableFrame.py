from tkinter import ALL, Canvas, Scrollbar
from tkinter.ttk import Frame

from platform import system as os_name


class ScrollableFrame(Frame):
    """
    A wrapper for the Frame class to make it scrollable.
    To make use of this fuctionality, pack anything into the .frame Frame of
    this object
    """
    def __init__(self, master, *args, **kwargs):
        self.master = master
        Frame.__init__(self, self.master, *args, **kwargs)

        self.grid(sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.vsb = Scrollbar(self, orient="vertical")
        self.vsb.grid(row=0, column=1, sticky='ns')

        if os_name() == 'Windows':
            self.canvas = Canvas(self, bd=0, yscrollcommand=self.vsb.set,
                                 highlightthickness=0)
        else:
            self.canvas = Canvas(self, bd=0, yscrollcommand=self.vsb.set,
                                 bg='#E9E9E9', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # everything will go in this frame
        self.frame = Frame(self.canvas)
        self.frame.grid(row=0, column=0, sticky='nsew')

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.vsb.config(command=self.canvas.yview)

        self.bind("<Configure>", self.configure_view)

        # mouse wheel scroll bindings c/o Mikhail. T on stackexchange:
        # https://stackoverflow.com/a/37858368
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.vsb.get() != (0.0, 1.0):
            if os_name() == 'Windows':
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                         "units")
            else:
                self.canvas.yview_scroll(-event.delta, "units")

    def configure_view(self, event=None, move_to_bottom=False):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        if move_to_bottom:
            self.canvas.yview_moveto(1.0)

    def reattach(self):
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")


if __name__ == "__main__":
    from tkinter import Label, W, Button, Tk

    class main(Frame):
        def __init__(self, master):
            self.master = master
            Frame.__init__(self, self.master)

            self.df = Frame(self.master)

            self.last1 = 20
            self.last2 = 40

            self.sf = ScrollableFrame(self.master)
            self.sf.grid(row=0, column=0)
            Button(self.master, text="add", command=self.add_1).grid(
                row=1, column=0)

            self.sf2 = ScrollableFrame(self.master)
            self.sf2.grid(row=0, column=1)
            Button(self.master, text="add2", command=self.add_2).grid(
                row=1, column=1)

            for i in range(20):
                lbl = Label(self.sf.frame, text="hi {0}".format(i))
                lbl.grid(row=i, sticky=W)
            for i in range(40):
                lbl = Label(self.sf2.frame, text="there {0}".format(i))
                lbl.grid(row=i, sticky=W)

            self.master.grid_rowconfigure(0, weight=1)
            self.master.grid_columnconfigure(0, weight=1)
            self.master.grid_columnconfigure(1, weight=1)

        def add_1(self):
            lbl = Label(self.sf.frame, text="added")
            lbl.grid(column=0, row=self.last1)
            self.last1 += 1
            self.sf.configure_view(move_to_bottom=True)

        def add_2(self):
            lbl = Label(self.sf2.frame, text="added")
            lbl.grid(column=0, row=self.last2)
            self.last2 += 1
            self.sf2.configure_view()

    root = Tk()
    m = main(master=root)
    m.mainloop()
