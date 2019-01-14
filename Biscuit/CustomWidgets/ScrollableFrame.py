from tkinter import ALL, Canvas, Scrollbar
from tkinter.ttk import Frame

from platform import system as os_name

from Biscuit.utils.constants import OSCONST


class ScrollableFrame(Frame):
    """
    A wrapper for the Frame class to make it scrollable.
    To make use of this fuctionality, pack anything into the .frame Frame of
    this object
    """
    def __init__(self, master, *args, **kwargs):
        self.master = master
        Frame.__init__(self, self.master, *args, **kwargs)

        # Block resizing. This is required because we bind the resizing code to
        # a <Configure> tag. This would result in one resizing to a specific
        # size to call self.configure_view again but with no arguments.
        self.block_resize = False

        self.grid(sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.vsb = Scrollbar(self, orient='vertical')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.hsb = Scrollbar(self, orient='horizontal')
        self.hsb.grid(row=1, column=0, sticky='ew')

        self.canvas = Canvas(self, bd=0, yscrollcommand=self.vsb.set,
                             xscrollcommand=self.hsb.set,
                             bg=OSCONST.CANVAS_BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # everything will go in this frame
        self.frame = Frame(self.canvas)
        self.frame.grid(row=0, column=0, sticky='nsew')

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.vsb.config(command=self.canvas.yview)
        self.hsb.config(command=self.canvas.xview)

        self.bind("<Configure>", self.configure_view)

        # mouse wheel scroll bindings c/o Mikhail. T on stackexchange:
        # https://stackoverflow.com/a/37858368
        self.bind('<Enter>', self._bind_to_mousewheel)
        self.bind('<Leave>', self._unbind_to_mousewheel)

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.vsb.get() != (0.0, 1.0):
            if os_name() == 'Windows':
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                         "units")
            else:
                self.canvas.yview_scroll(-event.delta, "units")

    def configure_view(self, event=None, move_to_bottom=False,
                       max_size=(None, None), resize_canvas='xy'):
        """
        Configure the size of the scrollable frame.

        Parameters
        ----------
        move_to_bottom : bool
            Whether or not to move the scroll bar all the way to the bottom.
        max_size : tuple of int's
            Maximum size that the scrollable canvas can be. This is a tuple of
            length 2. (X, Y).
        resize_canvas : str
            The directions along which the scrollable canvas should be
            stretched. One of `'x'`, `'y'`, or `'xy'` for the x-direction,
            y-direction, or both respectively.
        """
        bbox = self.canvas.bbox(ALL)
        x_size = None
        y_size = None
        if 'x' in resize_canvas:
            if max_size[0] is not None:
                x_size = min(max_size[0], bbox[2])
            else:
                x_size = bbox[2]
        if 'y' in resize_canvas:
            if max_size[1] is not None:
                y_size = min(max_size[1], bbox[3])
            else:
                y_size = bbox[3]
        self._resize_canvas(x_size, y_size)
        if move_to_bottom:
            self.canvas.yview_moveto(1.0)
        self.canvas.config(scrollregion=bbox)

    def _resize_canvas(self, width, height):
        """Resize the canvas to the specified size

        Parameters
        ----------
        width : int
            Width of the frame.
        height : int
            Height of the frame.
        """
        if not self.block_resize:
            if width is not None or height is not None:
                self.block_resize = True
            else:
                self.block_resize = False
            canvas_config = dict()
            if width is not None:
                canvas_config['width'] = width
            if height is not None:
                canvas_config['height'] = height
            self.canvas.config(**canvas_config)

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
