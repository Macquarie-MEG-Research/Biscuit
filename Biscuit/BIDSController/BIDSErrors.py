class NoProjectError(Exception):
    pass


class NoSubjectError(Exception):
    pass


class NoSessionError(Exception):
    pass


class NoScanError(Exception):
    pass


class IDError(Exception):
    pass


class MappingError(Exception):
    """Raised when the folder structure doesn't match the BIDS standard."""
    pass
