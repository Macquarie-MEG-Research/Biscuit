""" some OS dependent constants """

from platform import system as os_name
import os

OSNAMEMAP = {'Windows': 'WIN',
             'Linux': 'LNX',
             'Darwin': 'MAC'}   # TODO: confirm on other ios versions


class OSConstMap():
    """ Class which provides values of constants in an OS-dependent manner """
    def __init__(self):
        self.os = OSNAMEMAP.get(os_name(), 'MAC')

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getattr__(self, name):
        """ Retreive the required value

        Names will be suffixed by '_<OS>', so we want to just get the os
        dependent version
        If the variable is assigned in a non-OS-dependent manner (ie. no
        suffix then this will not be called and the value will be retreived
        directly)

        Parameters
        ----------
        name : str
            Name of the variable without an OS identifier
        """
        os_dep_name = name + '_' + self.os
        return self.__dict__[os_dep_name]


OSCONST = OSConstMap()

# tkinter.canvas background colour
OSCONST.CANVAS_BG_WIN = None        # System default ('#F0F0F0')
OSCONST.CANVAS_BG_MAC = '#ECECEC'
OSCONST.CANVAS_BG_LNX = '#D9D9D9'

# tkinter.entry background colour (I think?)
OSCONST.TEXT_BG_WIN = '#F0F0F0'
OSCONST.TEXT_BG_MAC = '#E9E9E9'
OSCONST.TEXT_BG_LNX = '#D9D9D9'

# tkinter.entry readonlybackground colour
OSCONST.TEXT_RONLY_BG_WIN = None
OSCONST.TEXT_RONLY_BG_MAC = '#E0E0E0'
OSCONST.TEXT_RONLY_BG_LNX = None

# keyboard shortcut to add a new row in the widget table
OSCONST.ADDROW_WIN = '<Control-n>'
OSCONST.ADDROW_MAC = '<Command-n>'
OSCONST.ADDROW_LNX = '<Control-n>'

# user directory
try:
    OSCONST.USRDIR_WIN = os.path.join(os.getenv('APPDATA'), 'Biscuit')
except TypeError:
    pass
OSCONST.USRDIR_MAC = os.path.join(os.path.expanduser('~'), 'Library',
                                  'Biscuit')
OSCONST.USRDIR_LNX = '~/.Biscuit'  # dummy for now

# biscuit icon file
OSCONST.ICON = 'assets/bisc.png'
OSCONST.ICON_GIF = 'assets/bisc.gif'

# ttk.treeview text size
OSCONST.TREEVIEW_TEXT_SIZE_WIN = 10
OSCONST.TREEVIEW_TEXT_SIZE_MAC = 13
OSCONST.TREEVIEW_TEXT_SIZE_LNX = 12
