from tkinter import Label, Checkbutton, Frame, ALL
from tkinter import StringVar, IntVar, DoubleVar, BooleanVar
from tkinter import Entry as tkEntry        # import this specifically like this because we can actually set the bg colour *sigh*
from tkinter.ttk import Label, Checkbutton, Frame


# maybe create a super class for all these to allow for easier isinstance(~)-ing?

class InfoMaster():
    def __init__(self, master, data):
        self._master = master

        self._label = None
        self._value = None
    
    def set_bads_callback(self, bad_values=None, parent=None):
        pass

    @property
    def label(self):
        return self._label

    @property
    def value(self):
        return self._value

    @property
    def master(self):
        return self._master

class InfoEntry(InfoMaster):
    def __init__(self, master, data):
        super(InfoEntry, self).__init__(master, data)
        #self._master = master

        # draw the label and entry box
        self._label = Label(self._master, text = "{0}: ".format(data[0]))
        self._value = tkEntry(self._master, textvariable = data[1])
    
    def set_bads_callback(self, bad_values=[''], parent=None):
        """
        bad_value is a list containing any values that will cause the verification to indicate the value is invalid
        """
        vcmd = self._value.register(self.set_background)
        self.bad_values = bad_values
        self.parent = parent    # the FileInfo object this entry provides the data for
        self._value.configure(validate=ALL, validatecommand=(vcmd, '%P', '%s'))

    def set_background(self, value_if_allowed, prior_value):
        print(value_if_allowed)
        if value_if_allowed not in self.bad_values:
            self._value.config({'background': "White"})
        else:
            self._value.config({'background': "Red"})
        # we also want to get the parent (which will hopefully be an InfoContainer object)
        # to run the bids verification function.
        self.parent.parent.check_bids_ready()
        return True

class InfoLabel(InfoMaster):
    def __init__(self, master, data):
        super(InfoLabel, self).__init__(master, data)

        # draw the label and entry box
        self._label = Label(self._master, text = "{0}: ".format(data[0]))
        self._value = Label(self._master, text = data[1])

class InfoChoice(InfoMaster):
    def __init__(self, master, data):
        super(InfoChoice, self).__init__(master, data)

        self._label = Label(self._master, text = "{0}: ".format(data[0]))
        self._value = Checkbutton(self._master, variable = data[1])

class InfoList(InfoMaster):
    def __init__(self, master, data):
        super(InfoList, self).__init__(master, data)
        
        self._label = Label(self._master, text = "{0}: ".format(data[0]))
        self._value = Frame(self._master)
        self._value.grid()
        if len(data[1]) != 0:
            for value in data[1]:
                # consider just labels for now...
                lbl = Label(self._value, text=value, wraplength=400)        # make the wrap length dynamic?? Ref'd to the parent size?
                lbl.grid(row=self._value.grid_size()[1])      # add to the end
        else:
            lbl = Label(self._value, text="None", foreground="Red")      
            lbl.grid(row=self._value.grid_size()[1])