from tkinter import *
from tkinter.ttk import *
import threading
import shutil

from platform import system as os_name

from os.path import isdir, basename, join

class EnhancedTreeview(Treeview):
    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(EnhancedTreeview, self).__init__(self.master, *args, **kwargs)

        self.root_path = ""

    def enhance(self, *args, **kwargs):
        # main function that allows for extra functionality to be built on.
        # Since the __init__ passes all kwargs to tcl, an error occurs if you try
        # and extend the functionality at creation

        # we will add functionality here sequentially

        # first set the keypress bindings as we will assume they want to happen first
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

    def get_dnd_selection(self):
        # this will currently get the previously selected entry
        return self.selection()

    def get_dnd_drop(self, source, selection, event):
        destination_id = self.identify_row(event.y)

        # if the destination is a path, then move the selected files there
        if isdir(self.item(destination_id)['values'][1]):
            for sid in selection:
                item = self.item(sid)
                shutil.move(item['values'][1], self.item(destination_id)['values'][1])
                self.move(sid, destination_id, self._get_insertion_index(sid, destination_id))
                self.item(sid, values=[item['values'][0], join(self.item(destination_id)['values'][1], '{0}{1}'.format(item['text'], item['values'][0]))])
        else:
            # move the selected file to the same directory as the one the file is in
            parent = self.parent(destination_id)
            for sid in selection:
                if self.parent(sid) != parent:
                    # only need to try move if the folder is actually different
                    if parent == '':
                        # this is the root directory
                        destination_path = self.root_path
                    else:
                        destination_path = self.item(destination_id)['values'][1]
                    item = self.item(sid)
                    shutil.move(item['values'][1], destination_path)
                    self.move(sid, parent, self._get_insertion_index(sid, parent))
                    # we also need to modify the path that the entry in the treeview has:
                    self.item(sid, values=[item['values'][0], join(destination_path, '{0}{1}'.format(item['text'], item['values'][0]))])

    def _add_dnd(self):
        if self.allow_dnd:
            self.dnd_manager = DNDManager(self)
        else:
            self.dnd_manager = None

    def _add_scrollbars(self):
        for orient in self.scrollbars:
            if orient == 'x':
                xsb = Scrollbar(self.master, orient = HORIZONTAL, command = self.xview)
                xsb.pack(side = BOTTOM, fill = X)
                #xsb.grid(row=2,column=10, rowspan=10, sticky="ns", in_=self.master)
                self.configure(xscroll=xsb.set)
            if orient == 'y':
                ysb = Scrollbar(self.master, orient = VERTICAL, command = self.yview)
                #ysb.grid(row=14,column=0, rowspan=2, sticky="ew", in_=self.master)
                ysb.pack(side = RIGHT, fill = Y)
                self.configure(yscroll=ysb.set)

    @property
    def OnRightClick(self):
        return self.rightclick_func
    
    @OnRightClick.setter
    def OnRightClick(self, func):
        # set the event to be processed when an entry is right-clicked
        # we need to determine the operating system here and bind Button-2 is mac, and Button-3 if windows
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

    def ordered_insert(self, parent, *args, **kwargs):
        # allows for objects to be inserted in the correct location alphabetically
        # they will be sorted by their text fields
        # this should be extended so that it is sorted by text > then any values in order
        sort_text = kwargs.get('text', None)
        if sort_text is not None:
            # only iterate over the children that are folders
            for i, child in enumerate([i for i in self.get_children(parent) if isdir(self.item(i)['values'][1])]):
                print(self.item(child)['text'], sort_text, sort_text < self.item(child)['text'])
                if sort_text < self.item(child)['text']:
                    index = i
                    break
            else:
                index = i + 1
            
            return self.insert(parent, index, *args, **kwargs)

    def _get_insertion_index(self, child_sid, parent_sid):
        """
        Find the index the object should be inserted at so that it remains in alphabetical order in the new location
        """
        child_fname = basename(self.item(child_sid)['values'][1])
        for index, child in enumerate(self.get_children(parent_sid)):
            if child_fname < basename(self.item(child)['values'][1]):
                return index
        else:
            return index + 1        # one more than the total length of the list

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
            self.mouseclick_thread = threading.Timer(interval=delay, function=func, args=[event])
            self.mouseclick_thread.start()

    def _add_bindings(self):
        self.master.bind("<ButtonPress-1>", lambda event: self._wait_then_run(0.15, self.on_start, event), add='+')
        self.master.bind("<B1-Motion>", self.on_drag, add='+')
        self.master.bind("<ButtonRelease-1>", self.on_drop, add='+')
        self.master.configure(cursor="hand1")

    def on_start(self, event):
        self.activated = True
        self.start_widget = event.widget.winfo_containing(*event.widget.winfo_pointerxy())
        self.initial_selection = self.start_widget.get_dnd_selection()
        self.popup = Toplevel(bd=1, background='lightblue')
        self.popup.wm_attributes('-alpha',0.9)
        #self.popup.transient()
        self.popup.overrideredirect(1)      # forces the top level to have no border etc
        self.popup.withdraw()
        xy = event.x_root+16, event.y_root+10
        self.popup.geometry("+%d+%d" % xy)
        self.popup.deiconify()
        self.popup.lift()
        file_label = Label(self.popup, text=self.start_widget.item(self.initial_selection[0])['text'])
        file_label.config(background='lightblue')
        file_label.pack(side=LEFT)

    def on_drag(self, event):
        # you could use this method to move a floating window that
        # represents what you're dragging
        #print("What a drag!")
        try:
            # this can throw an error if the user very quickly clicks and moves the mouse
            xy = event.x_root+16, event.y_root+10
            self.popup.geometry("+%d+%d" % xy)
        except:
            # if this happens we want to just ignore it
            pass

    def on_drop(self, event):
        # cancel the mouseclick_thread. If it hasn't completed then it won't. But if it has nothing will happen
        self.mouseclick_thread.cancel()
        try:
            self.popup.destroy()
        except:
            # it probably doesn't exist in this case...
            pass
        # find the widget under the cursor
        if self.activated == True:
            self.finish_widget = event.widget.winfo_containing(*event.widget.winfo_pointerxy())
            # pass the start widget info and event to the widget the cursor was dropped on
            #try:
            self.finish_widget.get_dnd_drop(self.start_widget, self.initial_selection, event)
            #except:
            #    print("widget you dropped on doesn't support DND!")
        
        # finish up by setting the DNDManager to inactive again
        self.activated = False