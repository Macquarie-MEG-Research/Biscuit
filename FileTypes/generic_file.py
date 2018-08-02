from .FileInfo import FileInfo


class generic_file(FileInfo):
    """
    Class for generic files that do not need much to happen with them
    (ie. just view, whatever...)
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(generic_file, self).__init__(id_, file, *args, **kwargs)
        self._type = 'generic'
        self.requires_save = False
        # any data tpe in the following list will automatically be assigned
        # the .display_raw = True property
        # they will also be not be specificed as unknown
        self.types_to_display_raw = ['.txt', '.m', '.py']

    def load_data(self):
        pass

    @property
    def dtype(self):
        return self._type

    @dtype.setter
    def dtype(self, value):
        # we will allow setting of type for this particular file type
        # as we want it to be able to be set whenever
        self._type = value
        if value in self.types_to_display_raw:
            self.display_raw = True
            self.unknown_type = False
        else:
            self.display_raw = False
            self.unknown_type = True
