from tkinter import StringVar, IntVar, DoubleVar, BooleanVar, Variable, TclError

from collections import OrderedDict

from struct import unpack

from .FileInfo import FileInfo

GAINS = [1, 2, 5, 10, 20, 50, 100, 200]

class con_file(FileInfo):
    """
    .con specific file container.
    """
    def __init__(self, id_, file, *args, **kwargs):
        super(con_file, self).__init__(id_, file, *args, **kwargs)

        self._type = '.con'

        #if self._auto_preload_data:
        #    self.load_data()

        # have as a property of the info so that it is drawn automatically

        # set any optional info
        self.optional_info['Is Junk'] = BooleanVar()

        # set any required info
        self.required_info['Acquisition'] = StringVar()
        self.required_info['associated_mrks'] = []       # these will be mrk_file objects

        # set any particular bad values
        # The keys of this dictionary must match the keys in the required info
        self.bad_values['Acquisition'] = {'values':['']}       # remove dtypes??
        self.bad_values['associated_mrks'] = {'values':[[]]}


    def load_data(self):

        # reads in various other pieces of information required
        with open(self.file, 'rb') as file:
            # let's get the gain:
            file.seek(0x70)
            offset = unpack('i', file.read(4))[0]
            file.seek(offset)
            amp_data = unpack('i', file.read(4))[0]
            gain1 = (amp_data & 0x00007000) >> 12
            gain2 = (amp_data & 0x70000000) >> 28
            gain3 = (amp_data & 0x07000000) >> 24
            self.info['gains'] = (GAINS[gain1], GAINS[gain2], GAINS[gain3])

            # get the InsitutionName and ManufacturersModelName:
            # code taken pretty much directly from the kit.py script in mne
            file.seek(0x20C)
            system_name = unpack('128s', file.read(128))[0].decode()
            model_name = unpack('128s', file.read(128))[0].decode()
            system_name = system_name.replace('\x00', '')
            #system_name = system_name.strip().replace('\n', '/')
            model_name = model_name.replace('\x00', '')
            #model_name = model_name.strip().replace('\n', '/')
            self.info['Insitution name'] = system_name
            self.info['Model name'] = model_name
    
    def check_complete(self):
        """
        This returns the list of bad values.
        If there are none then an empty list will be returned

        Actually, may be able to get this to be generic by using the bad_values dictionary...
        """

        # personalised check function for .con files
        # we need to make sure that the run number is not equal to 0:
        bads = []
        for key in self.bad_values:
            data = self.required_info.get(key, None)
            if data is not None:
                if isinstance(data, Variable):
                    # handle the Variable style objects differently as we need to call .get() on them
                    try:
                        if data.get() in self.bad_values[key]['values']:
                            bads.append((key, data.get()))
                    except TclError:
                        # getting an invalid value. Add to bads
                        bads.append((key, ''))
                else:
                    if data in self.bad_values[key]['values']:
                        bads.append((key, data))
        return bads