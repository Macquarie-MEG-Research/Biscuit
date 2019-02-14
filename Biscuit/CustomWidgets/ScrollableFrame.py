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
    block = False

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
        self.hsb = Scrollbar(self, orient='horizontal')

        self.drawn_scrollbars = []

        self.canvas = Canvas(self, bd=0, bg=OSCONST.CANVAS_BG,
                             highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # configure scroll bars
        self.hsb.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hsb.set)
        self.vsb.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vsb.set)

        # everything will go in this frame
        self.frame = Frame(self.canvas)
        self.frame.grid(row=0, column=0, sticky='nsew')

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.bind("<Configure>", self.configure_view)

        # mouse wheel scroll bindings c/o Mikhail. T on stackexchange:
        # https://stackoverflow.com/a/37858368
        self.bind('<Enter>', self._bind_to_mousewheel)
        self.bind('<Leave>', self._unbind_to_mousewheel)

#region public methods

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
            # find the new x size to draw
            if max_size[0] is not None:
                x_size = min(max_size[0], bbox[2])
            else:
                x_size = bbox[2]
        if 'y' in resize_canvas:
            # find the new y size to draw
            if max_size[1] is not None:
                y_size = min(max_size[1], bbox[3])
            else:
                y_size = bbox[3]

        self._resize_canvas(x_size, y_size)

        xview_size = int(self.canvas.config('width')[4])
        yview_size = int(self.canvas.config('height')[4])

        # determine if x scroll bar has to be drawn
        if bbox[2] > xview_size and 'x' not in self.drawn_scrollbars:
            self._config_scrollbars('x')
        elif bbox[2] <= xview_size and 'x' in self.drawn_scrollbars:
            self._config_scrollbars('x', False)
        # determine if y scroll bar has to be drawn
        if bbox[3] > yview_size and 'y' not in self.drawn_scrollbars:
            self._config_scrollbars('y')
        elif bbox[3] <= yview_size and 'y' in self.drawn_scrollbars:
            self._config_scrollbars('y', False)

        if move_to_bottom:
            self.canvas.yview_moveto(1.0)

        self.canvas.config(scrollregion=bbox)

    def reattach(self):
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

#region private methods

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _config_scrollbars(self, dir_, draw=True):
        """Only draw scroll bars if required.

        Parameters
        ----------
        dir_ : string : ('x', 'y')
            Direction to draw scroll bars in.
        draw : bool
            Whether to draw them or not (ie. un-draw)
        """
        if dir_ == 'x':
            if draw:
                self.hsb.grid(row=1, column=0, sticky='ew')
                self.hsb.config(command=self.canvas.xview)
                self.drawn_scrollbars.append('x')
            else:
                self.hsb.grid_forget()
                self.drawn_scrollbars.remove('x')
        if dir_ == 'y':
            if draw:
                print('drawing new scroll bar')
                self.vsb.grid(row=0, column=1, sticky='ns')
                self.vsb.config(command=self.canvas.yview)
                self.drawn_scrollbars.append('y')
            else:
                print('removing scroll bar')
                self.vsb.grid_forget()
                self.drawn_scrollbars.remove('y')

    def _on_mousewheel(self, event):
        if self.vsb.get() != (0.0, 1.0):
            if os_name() == 'Windows':
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                         "units")
            else:
                self.canvas.yview_scroll(-event.delta, "units")

    def _resize_canvas(self, width, height):
        """Resize the canvas to the specified size

        Parameters
        ----------
        width : int
            Width of the frame.
        height : int
            Height of the frame.
        """
        if self.block_resize:
            return
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

    def _unbind_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
