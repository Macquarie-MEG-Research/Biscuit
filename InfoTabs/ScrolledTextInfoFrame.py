from tkinter import WORD, END, StringVar
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button, Label
from pygments import lex
from pygments.lexers.python import Python3Lexer
from datetime import datetime


class ScrolledTextInfoFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(ScrolledTextInfoFrame, self).__init__(self.master, *args,
                                                    **kwargs)

        self.saved_time = StringVar()

        self._create_widgets()

        # the associated file
        self._file = None

    # This doesn't really work...
    def insert_tab(self, *event):
        # insert 4 spaces
        self.textentry.insert('insert', " " * 4)
        return "break"

    # TODO: rename the textentry
    def _create_widgets(self):
        # create a Text widget and read in the file
        self.textentry = ScrolledText(self, wrap=WORD)
        self.textentry.grid(column=0, row=0, columnspan=2, sticky='nsew')
        #self.textentry.bind("<Tab>", self.insert_tab)
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
        self.syn()

    def _update_savetime(self):
        self.saved_time.set("Last saved:\t{0}\t".format(self.file.saved_time))

    def syn(self, event=None):
        """
        # TODO: find source/reference this!!
        Allow for syntax highlighting
        """
        self.textentry.mark_set("range_start", "1.0")
        data = self.textentry.get("1.0", "end-1c")
        for token, content in lex(data, Python3Lexer()):
            #print(token, content)
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
