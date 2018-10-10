""" some OS dependent constants """

from platform import system as os_name

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

OSCONST.CANVAS_BG_WIN = None        # System default ('#F0F0F0')
OSCONST.CANVAS_BG_MAC = '#E9E9E9'   # TODO: confirm
OSCONST.CANVAS_BG_LNX = '#D9D9D9'   # TODO: confirm

OSCONST.TEXT_BG_WIN = '#F0F0F0'
OSCONST.TEXT_BG_MAC = '#E9E9E9'
OSCONST.TEXT_BG_LNX = '#D9D9D9'
