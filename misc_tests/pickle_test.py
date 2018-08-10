import pickle
from random import randint


class test():
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.id = randint(0, 10000)
        self._p = 3

    def __str__(self):
        return str('id: {0}'.format(self.id))

    def __getstate__(self):
        data = {}
        data['x'] = self.x
        data['y'] = self.y
        data['z'] = self.z
        return data

    def __setstate__(self, state):
        print('hi')
        self.__init__()
        self.x = state['x']
        self.y = state['y']
        self.z = state['z']


class ant(test):
    def __init__(self, x=0, y=0, z=0):
        super(ant, self).__init__(x, y, z)
        self.x = 5 * x

    def __str__(self):
        return "my id is {0}, my values are {1}".format(self.id, (self.x, self.y, self.z))


def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


f = ant(1, 2, 3)
print(f)
print(f._p)
with open('test.d', 'wb') as file:
    pickle.dump(f, file)

with open('test.d', 'rb') as file:
    new_f = pickle.load(file)
print(new_f)
print(new_f._p)
