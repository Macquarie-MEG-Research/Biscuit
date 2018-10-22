from tkinter import HORIZONTAL, RIGHT, Y, VERTICAL, LEFT, BOTTOM, X, W
from tkinter import Toplevel, Label, TclError
from tkinter import Entry as tkEntry
from tkinter.ttk import Treeview, Scrollbar
import threading
import shutil

from platform import system as os_name

from os.path import isdir, basename, join


class EnhancedTreeview(Treeview):
    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(EnhancedTreeview, self).__init__(self.master, *args, **kwargs)

        self.columns = ['#0'] + kwargs.get('displaycolumns', [])
        self.editable_columns = []

        self.root_path = ""
        self.entryPopup = None

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
        self.allow_dnd = kwargs.get("allow_dnd", False)
        self._add_dnd()
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

        """
        could do check boxes using the unicode characters u"\u2610" and
        u"\u2611", but will look bad
        self.check_columns = kwargs.get("check_columns", [])
        if self.check_columns != []:
            self.im_checked = PhotoImage(file='assets/checked.png')
            self.im_unchecked = PhotoImage(file='assets/unchecked.png')
            self.tag_configure("checked", image=self.im_checked)
            self.tag_configure("unchecked", image=self.im_unchecked)
            self.bind("<Button-1>>", self._toggle_checkbox, add='+')
        """

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

    def get_dnd_selection(self):
        # this will currently get the previously selected entry
        return self.selection()

    def get_dnd_drop(self, source, selection, event):
        destination_id = self.identify_row(event.y)

        # if the destination is a path, then move the selected files there
        if isdir(self.item(destination_id)['values'][1]):
            for sid in selection:
                item = self.item(sid)
                shutil.move(item['values'][1],
                            self.item(destination_id)['values'][1])
                self.move(sid, destination_id,
                          self._get_insertion_index(sid, destination_id))
                self.item(sid, values=[item['values'][0],
                          join(self.item(destination_id)['values'][1],
                               '{0}{1}'.format(item['text'],
                                               item['values'][0]))])
        else:
            # move the selected file to the same directory as the one the file
            # is in
            parent = self.parent(destination_id)
            for sid in selection:
                if self.parent(sid) != parent:
                    # only need to try move if the folder is actually different
                    if parent == '':
                        # this is the root directory
                        destination_path = self.root_path
                    else:
                        destination_path = self.item(
                            destination_id)['values'][1]
                    item = self.item(sid)
                    shutil.move(item['values'][1], destination_path)
                    self.move(sid, parent,
                              self._get_insertion_index(sid, parent))
                    # we also need to modify the path that the entry in the
                    # treeview has:
                    self.item(sid, values=[item['values'][0],
                              join(destination_path,
                                   '{0}{1}'.format(item['text'],
                                                   item['values'][0]))])

    def _add_dnd(self):
        if self.allow_dnd:
            self.dnd_manager = DNDManager(self)
        else:
            self.dnd_manager = None

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
        print('popup', self.entryPopup)
        if self.entryPopup is not None:
            try:
                self.entryPopup.onExit(event)
            except (AttributeError, TclError):
                # In this case I dunno, but just pass
                pass
    """
    def _toggle_checkbox(self, event):
        # find out what row and column was clicked on
        rowid = self.identify_row(event.y)
        column_num = self.identify_column(event.x)
        column = self.column(column_num, option='id')
        if column_num == '#0':
            column = column_num
        # we only want to allow editing if the user has specified the column
        # should be editable
        if column in self.check_columns or column_num in self.check_columns:
            pass
    """

    @property
    def OnRightClick(self):
        return self.rightclick_func

    @OnRightClick.setter
    def OnRightClick(self, func):
        # set the event to be processed when an entry is right-clicked
        # we need to determine the operating system here and bind Button-2 is
        # mac, and Button-3 if windows
        if os_name() == 'Windows':
            self.bind("<Button-3>", func, add='+')
        else:
            self.bind("<Button-2>", func, add='+')

    @property
    def OnLeftClick(self):
        return self.leftclick_func

    @OnLeftClick.setter
    def OnLeftClick(self, value):
        # set the event to be processed when an entry is clicked
        self.bind("<<TreeviewSelect>>", self.leftclick_func, add='+')

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

    def _get_open_folders(self, parent=''):
        open_folders = []
        for sid in self.get_children(parent):
            if self.item(sid, option='open'):
                # check if the children of the open folder itself has any open
                # folders
                open_folders.append(self._get_open_folders(sid))
                open_folders.append(sid)
        return open_folders

    def ordered_insert(self, parent, *args, **kwargs):
        """
        Allows for objects to be inserted in the correct location
        alphabetically. They will be sorted by their text fields.
        This should be extended so that it is sorted by text > then any values
        in order.
        This will also only allow for insertion of folders in the correct place

        Returns the id of the object that has been inserted
        """
        sort_text = kwargs.get('text', None)
        if sort_text is not None:
            # only iterate over the children that are folders
            child_folders = [i for i in self.get_children(parent) if
                             isdir(self.item(i)['values'][1])]
            if len(child_folders) != 0:
                for i, child in enumerate(child_folders):
                    if sort_text < self.item(child)['text']:
                        index = i
                        break
                else:
                    index = i + 1
            else:
                index = 0

            return self.insert(parent, index, *args, **kwargs)

    def _get_insertion_index(self, child_sid, parent_sid):
        """
        Find the index the object should be inserted at so that it remains in
        alphabetical order in the new location
        """
        child_fname = basename(self.item(child_sid)['values'][1])
        for index, child in enumerate(self.get_children(parent_sid)):
            if child_fname < basename(self.item(child)['values'][1]):
                return index
        else:
            # one more than the total length of the list
            return index + 1


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


class DNDManager():
    """
    A manager to control drag and drop.
    For the meantime, this will only support dragging of objects in a treeview
    """
    def __init__(self, master):
        self.master = master
        self._add_bindings()

        self.activated = False

        self.start_widget = None    # actual widget objects
        self.initial_selection = None
        self.finish_widget = None
        self.final_selection = None
    
    def _wait_then_run(self, delay, func, event):
        # we need to make sure we have selected an actual row...
        if self.master.identify_row(event.y) != "":
            self.mouseclick_thread = threading.Timer(interval=delay,
                                                     function=func,
                                                     args=[event])
            self.mouseclick_thread.start()

    def _add_bindings(self):
        self.master.bind("<ButtonPress-1>",
                         lambda event: self._wait_then_run(
                             0.15, self.on_start, event), add='+')
        self.master.bind("<B1-Motion>", self.on_drag, add='+')
        self.master.bind("<ButtonRelease-1>", self.on_drop, add='+')
        self.master.configure(cursor="hand1")

    def on_start(self, event):
        self.activated = True
        self.start_widget = event.widget.winfo_containing(
            *event.widget.winfo_pointerxy())
        self.initial_selection = self.start_widget.get_dnd_selection()
        self.popup = Toplevel(bd=1, background='lightblue')
        self.popup.wm_attributes('-alpha', 0.9)
        #self.popup.transient()
        # forces the top level to have no border etc:
        self.popup.overrideredirect(1)
        self.popup.withdraw()
        xy = event.x_root + 16, event.y_root + 10
        self.popup.geometry("+%d+%d" % xy)
        self.popup.deiconify()
        self.popup.lift()
        file_label = Label(
            self.popup,
            text=self.start_widget.item(self.initial_selection[0])['text'])
        file_label.config(background='lightblue')
        file_label.pack(side=LEFT)

    def on_drag(self, event):
        # you could use this method to move a floating window that
        # represents what you're dragging
        #print("What a drag!")
        try:
            # this can throw an error if the user very quickly clicks and moves
            # the mouse
            xy = event.x_root + 16, event.y_root + 10
            self.popup.geometry("+%d+%d" % xy)
        except:
            # if this happens we want to just ignore it
            pass

    def on_drop(self, event):
        # cancel the mouseclick_thread. If it hasn't completed then it won't.
        # But if it has nothing will happen
        self.mouseclick_thread.cancel()
        try:
            self.popup.destroy()
        except:
            # it probably doesn't exist in this case...
            pass
        # find the widget under the cursor
        if self.activated is True:
            self.finish_widget = event.widget.winfo_containing(
                *event.widget.winfo_pointerxy())
            # pass the start widget info and event to the widget the cursor was
            #  dropped on
            #try:
            self.finish_widget.get_dnd_drop(self.start_widget,
                                            self.initial_selection, event)
            #except:
            #    print("widget you dropped on doesn't support DND!")

        # finish up by setting the DNDManager to inactive again
        self.activated = False
