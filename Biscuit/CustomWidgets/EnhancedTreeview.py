from tkinter import HORIZONTAL, RIGHT, Y, VERTICAL, BOTTOM, X, W
from tkinter import TclError
from tkinter import Entry as tkEntry
from tkinter.ttk import Treeview, Scrollbar

import os.path as op
from platform import system as os_name

from Biscuit.utils.constants import OSCONST


class EnhancedTreeview(Treeview):
    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(EnhancedTreeview, self).__init__(self.master, *args, **kwargs)

        self.columns = ['#0'] + kwargs.get('displaycolumns', [])
        self.editable_columns = []

        self.entryPopup = None

#region public methods

    def add_tags(self, id_, tags):
        """
        Add the tag specified to the list of tags for the object with id_
        """
        curr_tags = list(self.item(id_, option='tags'))
        if isinstance(tags, list):
            for t in tags:
                if t not in curr_tags:
                    curr_tags.append(t)
        else:
            if tags not in curr_tags:
                curr_tags.append(t)
        self.item(id_, tags=curr_tags)

    def all_children(self, item=''):
        """
        This is a generator that will yield the ids of all the children
        of the treeview recursively
        They will not necessarily be in order. The folders will be after the
        files listed in the folder
        """
        children = self.get_children(item)
        if len(children) != 0:
            for sid in children:
                for child in self.all_children(sid):
                    yield child
            yield item
        else:
            yield item

    def doubleclick_func(self, event):
        ''' Executed, when a row is double-clicked. Opens
        read-only EntryPopup above the item's column, so it is possible
        to select text '''
        print('double clicked')

        # close previous popups
        #self.master.destroyPopups()

        # what row and column was clicked on
        rowid = self.identify_row(event.y)
        column_num = self.identify_column(event.x)
        column = self.column(column_num, option='id')
        if column_num == '#0':
            column = column_num
        # we only want to allow editing if the user has specified the column
        # should be editable
        if column in self.editable_columns:
            # get column position info
            x, y, width, height = self.bbox(rowid, column)

            # y-axis offset
            pady = height // 2

            # place Entry popup properly
            if column == '#0':
                text = self.item(rowid, 'text')
            else:
                text = self.item(rowid, 'values')[int(column_num[1:]) - 1]
            if text == '':
                text = u"\u2611"
            self.entryPopup = EntryPopup(self, text, (rowid, column_num))
            self.entryPopup.place(x=x, y=y + pady, width=width, anchor=W)

    def enhance(self, *args, **kwargs):
        # main function that allows for extra functionality to be built on.
        # Since the __init__ passes all kwargs to tcl, an error occurs if you
        # try and extend the functionality at creation

        # we will add functionality here sequentially

        # first set the keypress bindings as we will assume they want to happen
        # first
        #self.multiclick_func = kwargs.get("multiclick",None)
        self.leftclick_func = kwargs.get("leftclick", None)
        self.OnLeftClick = self.leftclick_func
        self.rightclick_func = kwargs.get("rightclick", None)
        self.OnRightClick = self.rightclick_func

        # now we can set others
        self.scrollbars = kwargs.get("scrollbars", [])
        self._add_scrollbars()
        sortable = kwargs.get("sortable", False)
        if sortable:
            # sortable can either just be a list of columns, or if just True
            # then the automatically determined visible columns are set as
            # sortable
            if not isinstance(sortable, list):
                for column in self.columns:
                    self.heading(
                        column,
                        command=lambda _col=column: self.treeview_sort_column(
                            _col, False))
            else:
                for column in sortable:
                    self.heading(
                        column,
                        command=lambda _col=column: self.treeview_sort_column(
                            _col, False))
        editable = kwargs.get("editable", False)
        if editable:
            # editable can either just be True (all entries editable), or a
            # list of column names
            if isinstance(editable, list):
                self.editable_columns = editable
            else:
                # set as list of default columns
                self.editable_columns = self.columns
            # also bind the double click method
            self.bind("<Double-1>", self.doubleclick_func)
            # add to the treeview select bind to close the currently open
            # entry?
            self.bind("<<TreeviewSelect>>", self._close_entry, add='+')

    def remove_tags(self, id_, tags):
        curr_tags = list(self.item(id_, option='tags'))
        if isinstance(tags, list):
            for t in tags:
                if t in curr_tags:
                    curr_tags.remove(t)
        else:
            if tags in curr_tags:
                curr_tags.remove(t)
        self.item(id_, tags=curr_tags)

    def treeview_sort_column(self, col, reverse):
        # first, get the list of all open folders
        sort_folders = [''] + self._get_open_folders()

        for fid in sort_folders:
            if col != '#0':
                lst = [(self.set(k, col).lower(), k) for k in
                       self.get_children(fid)]
            else:
                lst = [(self.item(sid, option='text').lower(), sid) for
                       sid in self.get_children(fid)]
            lst.sort(reverse=reverse)

            # rearrange items in sorted positions
            for index, (_, k) in enumerate(lst):
                self.move(k, fid, index)

        # reverse sort next time
        self.heading(
            col, command=lambda: self.treeview_sort_column(col, not reverse))

#region private methods

    def _add_scrollbars(self):
        for orient in self.scrollbars:
            if orient == 'x':
                xsb = Scrollbar(self.master, orient=HORIZONTAL,
                                command=self.xview)
                xsb.pack(side=BOTTOM, fill=X)
                self.configure(xscroll=xsb.set)
            if orient == 'y':
                ysb = Scrollbar(self.master, orient=VERTICAL,
                                command=self.yview)
                ysb.pack(side=RIGHT, fill=Y)
                self.configure(yscroll=ysb.set)

    def _close_entry(self, event):
        """ un-draw an open entry if there is one """
        if self.entryPopup is not None:
            try:
                self.entryPopup.onExit(event)
            except (AttributeError, TclError):
                # In this case I dunno, but just pass
                pass

    def _get_insertion_index(self, child_sid, parent_sid):
        """
        Find the index the object should be inserted at so that it remains in
        alphabetical order in the new location
        """
        child_fname = op.basename(self.item(child_sid)['values'][1])
        for index, child in enumerate(self.get_children(parent_sid)):
            if child_fname < op.basename(self.item(child)['values'][1]):
                return index
        else:
            # one more than the total length of the list
            return index + 1

    def _get_open_folders(self, parent=''):
        open_folders = []
        for sid in self.get_children(parent):
            if self.item(sid, option='open'):
                # check if the children of the open folder itself has any open
                # folders
                open_folders.append(self._get_open_folders(sid))
                open_folders.append(sid)
        return open_folders

#region properties

    @property
    def OnRightClick(self):
        return self.rightclick_func

    @OnRightClick.setter
    def OnRightClick(self, func):
        # set the event to be processed when an entry is right-clicked
        self.bind(OSCONST.RIGHTCLICK, func, add='+')
        if os_name() == 'Darwin':
            self.bind('<Control-Button-1>', func, add='+')

    @property
    def OnLeftClick(self):
        return self.leftclick_func

    @OnLeftClick.setter
    def OnLeftClick(self, value):
        # set the event to be processed when an entry is clicked
        self.bind("<<TreeviewSelect>>", self.leftclick_func, add='+')


class EntryPopup(tkEntry):

    def __init__(self, master, text, entry_index, **kw):
        """
        Simple entry to go over the box in the treeview to allow entries to
        be edited
        parent is the treeview parent
        parent is a tuple of the format (row, column_id) so we can set the new
        value """
        super().__init__(master, **kw)
        self.entry_index = entry_index

        self.insert(0, text)
        self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False

        self.focus_force()
        self.bind("<Control-a>", self.selectAll)
        self.bind("<Return>", self.onExit)

    def selectAll(self, event):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'

    def onExit(self, event):
        """ Write the current value in the entry to the value and un-draw """
        value = self.get()
        if self.entry_index[1] == '#0':
            self.master.item(self.entry_index[0], text=value)
        else:
            old_vals = list(self.master.item(self.entry_index[0], 'values'))
            old_vals[int(self.entry_index[1][1:]) - 1] = value
            self.master.item(self.entry_index[0], values=old_vals)

        self.destroy()
