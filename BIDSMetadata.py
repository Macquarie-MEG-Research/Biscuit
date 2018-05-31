

class BIDSMetadata():
    """
    Essentially a container for all the information to do with a set of data
    that can be easily accesed and used to read/convert the data to BIDS format
    """
    def __init__(self):
        self.name = ""
        self.files = []