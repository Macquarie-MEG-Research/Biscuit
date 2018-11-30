class Version():
    """ Version object to allow for accurate comparisons of version numbers"""
    def __init__(self, major=0, minor=0, revision=0, build=0):
        self.major = major
        self.minor = minor
        self.revision = revision
        self.build = build

    def __str__(self):
        if self.build != 0:
            return '{0}.{1}.{2}-b{3}'.format(self.major, self.minor,
                                             self.revision, self.build)
        return '{0}.{1}.{2}'.format(self.major, self.minor, self.revision)

    def __eq__(self, other):
        if ((self.major == other.major) and (self.minor == other.minor) and
                (self.revision == other.revision) and
                (self.build == other.build)):
            return True
        return False

    def __gt__(self, other):
        if self.major > other.major:
            return True
        elif self.major == other.major:
            if self.minor > other.minor:
                return True
            elif self.minor == other.minor:
                if self.revision > other.revision:
                    return True
                elif self.revision == other.revision:
                    if self.build > other.build:
                        return True
        return False

    def __lt__(self, other):
        return not (self > other)

    def __ge__(self, other):
        return (self == other) & (self > other)

    def __le__(self, other):
        return (self == other) & (self < other)

    @classmethod
    def from_repr(cls, rep):
        """Return a Version object from a string representation."""
        rep = rep.replace('v', '')
        parts = rep.split('.')
        vers_list = []
        for part in parts:
            vers_list.extend(part.split('-'))
        # sanitize each value:
        for i in range(len(vers_list)):
            val = vers_list[i]
            if 'b' in val:
                vers_list[i] = int(val.replace('b', ''))
            else:
                vers_list[i] = int(val)
        return Version(*vers_list)
