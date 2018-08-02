from tkinter import Frame, Tk, Scrollbar, Canvas, ALL
#from tkinter.ttk import Frame, Scrollbar, Canvas


class ScrollableFrame(Frame):
    """
    A wrapper for the Frame class to make it scrollable.
    To make use of this fuctionality, pack anything into the .frame Frame of this object
    """
    def __init__(self, master, *args, **kwargs):
        self.master = master
        Frame.__init__(self, self.master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.vsb = Scrollbar(self, orient="vertical")
        self.vsb.grid(row=0, column=1, sticky='ns')

        self.canvas = Canvas(self, bd=0, yscrollcommand=self.vsb.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # everything will go in this frame
        self.frame = Frame(self.canvas, bd=0)
        self.frame.grid(row=0, column=0, sticky='nsew')

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.vsb.config(command=self.canvas.yview)
        self.canvas.columnconfigure(0, weight=1)

        #self.frame.bind("<Configure>", self.configure_view)

    def configure_view(self, event):
        #print('configing')
        #print(self.canvas.bbox(ALL), self.canvas.grid_bbox())
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def reattach(self):
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")


if __name__ == "__main__":
    from tkinter import Label, W

    class main(Frame):
        def __init__(self, master):
            self.master = master
            Frame.__init__(self, self.master)

            self.sf = ScrollableFrame(self.master)
            self.sf.grid(row=0)

            for i in range(10):
                lbl = Label(self.sf.frame, text="hi {0}".format(i))
                lbl.grid(row=i, sticky=W)

    root = Tk()
    m = main(master=root)
    m.mainloop()
