from tkinter import WORD, END, StringVar
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button, Label
from warnings import warn
try:
    from pygments import lex
    from pygments.lexers.python import Python3Lexer
    from pygments.lexers.matlab import MatlabLexer
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False
    warn("Python library `pygments` not found. This isn't an issue, however "
         "if you install it you can have nice syntax highlighting when "
         "opening files containing code such as matlab (.m) or python (.py) "
         "files.")
from datetime import datetime

from Biscuit.utils.utils import threaded


class ScrolledTextInfoFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(ScrolledTextInfoFrame, self).__init__(self.master, *args,
                                                    **kwargs)

        self.saved_time = StringVar()

        self.highlighter = Highlighter()

        self._create_widgets()

        # the associated file
        self._file = None

    # TODO: rename the textentry
    def _create_widgets(self):
        # create a Text widget and read in the file
        self.textentry = ScrolledText(self, wrap=WORD)
        self.textentry.grid(column=0, row=0, columnspan=2, sticky='nsew')
        for key, value in self.highlighter.style:
            self.textentry.tag_configure(key, foreground=value)
        self.save_label = Label(self, textvar=self.saved_time)
        self.save_label.grid(column=0, row=1, sticky='es')
        self.save_btn = Button(self, text="Save", command=self.save_file)
        self.save_btn.grid(column=1, row=1, sticky='es')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

    def update(self):
        self._update_savetime()
        self.textentry.delete(1.0, END)
        with open(self.file.file, 'r') as file:
            self.textentry.insert(END, file.read())
        if HAS_PYGMENTS:
            if self.highlighter.change_type(self.file.dtype):
                # remove current tags
                for tag in self.textentry.tag_names():
                    self.textentry.tag_configure(tag, foreground="#000000")
                for key, value in self.highlighter.style.items():
                    self.textentry.tag_configure(key, foreground=value)
            self.syn()

    def _update_savetime(self):
        self.saved_time.set("Last saved:\t{0}\t".format(self.file.saved_time))

    @threaded
    def syn(self, event=None):
        """
        Allow for syntax highlighting.
        Source: https://stackoverflow.com/a/30199105
        This will highlight the entire document once. Dynamic highlighting not
        yet supported.
        #TODO: (maybe?): https://stackoverflow.com/questions/32058760/improve-pygments-syntax-highlighting-speed-for-tkinter-text/32064481  # noqa

        This is threaded to hopefully stop it blocking the view from displaying
        and causing a race condition.
        """
        self.textentry.mark_set("range_start", "1.0")
        data = self.textentry.get("1.0", "end-1c")
        lexer = self.highlighter.lexer
        if lexer is not None:
            for token, content in lex(data, lexer()):
                self.textentry.mark_set("range_end",
                                        "range_start + %dc" % len(content))
                self.textentry.tag_add(str(token), "range_start", "range_end")
                self.textentry.mark_set("range_start", "range_end")

    def save_file(self):
        """ Write the current data in the text widget back to the file """
        file_contents = self.textentry.get("1.0", "end-1c")
        with open(self.file.file, 'w') as file:
            file.write(file_contents)
        savetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.file.saved_time = savetime
        self._update_savetime()
        # also re-apply the syntax highlighting
        self.syn()

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, other):
        """
        Set the file property to whatever the new file is.
        When this happens the update command will be called which will redraw
        the channel info list
        """
        # if the file is being set as a con_file continue
        if other != self._file:
            self._file = other
            self.update()


class Highlighter():
    def __init__(self):
        self.dtype = None

    @property
    def style(self):
        """ Returns the appropriate syntax highlighting colours """
        if self.dtype == '.py':
            return {"Token.Literal.String.Single": "#00AA00",
                    "Token.Literal.String.Double": "#00AA00",
                    "Token.Literal.String.Doc": "#00AA00",
                    "Token.Operator.Word": "#900090",
                    "Token.Comment.Single": "#DD0000",
                    "Token.Keyword": "#FF7700",
                    "Token.Keyword.Namespace": "#FF7700",
                    "Token.Name.Function": "#0000FF",
                    "Token.Name.Builtin": "#900090"}
        elif self.dtype == '.m':
            return {"Token.Literal.String": "#A020F0",
                    "Token.Comment": "#228B22",
                    "Token.Keyword": "#0000FF"}
        else:
            return dict()

    @property
    def lexer(self):
        if self.dtype == '.py':
            return Python3Lexer
        elif self.dtype == '.m':
            return MatlabLexer
        else:
            return None

    def change_type(self, dtype):
        """ sets the data type and returns true if the type has changed """
        if dtype != self.dtype:
            self.dtype = dtype
            return True
        else:
            return False
