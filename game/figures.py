class Figur:

    def __init__(self, size, shape, color, full, name):
        self.size = size
        self.shape = shape
        self.color = color
        self.full = full
        self.name = name

    def get_size(self):
        return self.size

    def get_shape(self):
        return self.shape

    def get_color(self):
        return self.color

    def get_full(self):
        return self.full

    def get_name(self):
        return self.name


f1 = Figur(size = 'high', shape = 'square', color = 'white', full = 1, name = 'f1')
f2 = Figur(size = 'high', shape = 'square', color = 'white', full = 0, name = 'f2')
f3 = Figur(size = 'low', shape = 'square', color = 'white', full = 1, name = 'f3')
f4 = Figur(size = 'low', shape = 'square', color = 'white', full = 0, name = 'f4')
f5 = Figur(size = 'high', shape = 'round', color = 'white', full = 1, name = 'f5')
f6 = Figur(size = 'high', shape = 'round', color = 'white', full = 0, name = 'f6')
f7 = Figur(size = 'low', shape = 'round', color = 'white', full = 1, name = 'f7')
f8 = Figur(size = 'low', shape = 'round', color = 'white', full = 0, name = 'f8')
f9 = Figur(size='high', shape = 'square', color = 'black', full = 1, name = 'f9')
f10 = Figur(size='high', shape = 'square', color = 'black', full = 0, name = 'f10')
f11 = Figur(size = 'low', shape = 'square', color = 'black', full = 1, name = 'f11')
f12 = Figur(size = 'low', shape = 'square', color = 'black', full = 0, name = 'f12')
f13 = Figur(size = 'high', shape = 'round', color = 'black', full = 1, name = 'f13')
f14 = Figur(size = 'high', shape = 'round', color = 'black', full = 0, name = 'f14')
f15 = Figur(size = 'low', shape = 'round', color = 'black', full = 1, name = 'f15')
f16 = Figur(size = 'low', shape = 'round', color = 'black', full = 0, name = 'f16')