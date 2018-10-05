from tkinter import Frame, WORD, END
from tkinter.scrolledtext import ScrolledText
from pygments import lex
from pygments.lexers.python import Python3Lexer


class ScrolledTextInfoFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(ScrolledTextInfoFrame, self).__init__(self.master, *args,
                                                    **kwargs)

        self._create_widgets()

        # the associated file
        self._file = None

    def _create_widgets(self):
            # create a Text widget and read in the file
            self.textentry = ScrolledText(self, wrap=WORD)
            self.textentry.grid(column=0, row=0, sticky='nsew')
            self.textentry.tag_configure("Token.Literal.String.Single",
                                         foreground="#00AA00")
            self.textentry.tag_configure("Token.Literal.String.Double",
                                         foreground="#00AA00")
            self.textentry.tag_configure("Token.Literal.String.Doc",
                                         foreground="#00AA00")
            self.textentry.tag_configure("Token.Operator.Word",
                                         foreground="#900090")
            self.textentry.tag_configure("Token.Comment.Single",
                                         foreground="#DD0000")
            self.textentry.tag_configure("Token.Keyword",
                                         foreground="#FF7700")
            self.textentry.tag_configure("Token.Keyword.Namespace",
                                         foreground="#FF7700")
            self.textentry.tag_configure("Token.Name.Function",
                                         foreground="#0000FF")
            self.textentry.tag_configure("Token.Name.Builtin",
                                         foreground="#900090")
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

    def update(self):
        self.textentry.delete(1.0, END)
        with open(self.file.file, 'r') as file:
            self.textentry.insert(END, file.read())
        self.syn()

    def syn(self, event=None):
        print('doing anything?')
        self.textentry.mark_set("range_start", "1.0")
        data = self.textentry.get("1.0", "end-1c")
        for token, content in lex(data, Python3Lexer()):
            #print(token, content)
            self.textentry.mark_set("range_end",
                                    "range_start + %dc" % len(content))
            self.textentry.tag_add(str(token), "range_start", "range_end")
            self.textentry.mark_set("range_start", "range_end")

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
