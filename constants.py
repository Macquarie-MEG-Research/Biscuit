""" some OS dependent constants """

from platform import system as os_name
import os

OSNAMEMAP = {'Windows': 'WIN',
             'Linux': 'LNX',
             'Darwin': 'MAC'}   # TODO: confirm on other ios versions


class OSConstMap():
    def __init__(self):
        self.os = OSNAMEMAP.get(os_name(), 'MAC')

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getattr__(self, name):
        # names will be suffixed by '_<OS>', so we want to just get the os
        # dependent version
        os_dep_name = name + '_' + self.os
        return self.__dict__[os_dep_name]


OSCONST = OSConstMap()

# tkinter.canvas background colour
OSCONST.CANVAS_BG_WIN = None        # System default ('#F0F0F0')
OSCONST.CANVAS_BG_MAC = '#E9E9E9'
OSCONST.CANVAS_BG_LNX = '#D9D9D9'

# tkinter.entry background colour (I think?)
OSCONST.TEXT_BG_WIN = '#F0F0F0'
OSCONST.TEXT_BG_MAC = '#E9E9E9'
OSCONST.TEXT_BG_LNX = '#D9D9D9'

# keyboard shortcut to add a new row in the widget table
OSCONST.ADDROW_WIN = '<Control-n>'
OSCONST.ADDROW_MAC = '<Command-n>'
OSCONST.ADDROW_LNX = '<Control-n>'

# user directory
OSCONST.USRDIR_WIN = os.path.join(os.getenv('APPDATA'), 'Biscuit')
OSCONST.USRDIR_MAC = os.path.join('~/Library/', 'Biscuit')
OSCONST.USRDIR_LNX = '~/.Biscuit'  # dummy for now

# biscuit icon file
OSCONST.ICON = 'assets/bisc.png'

# ttk.treeview text size
OSCONST.TREEVIEW_TEXT_SIZE_WIN = 10
OSCONST.TREEVIEW_TEXT_SIZE_MAC = 13
OSCONST.TREEVIEW_TEXT_SIZE_LNX = 12
