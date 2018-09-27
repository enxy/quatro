class Director:
    """ Manages the construction process."""
    def construct_figure(self, size, shape, full, color, name):
        self.builder = FigureBuilder()
        self.builder.build_figure(size, shape, full, color, name)

    def get_result(self):
        return self.builder.get_figure()

class Builder:
    """ Creates various features of figures."""
    def build_figure(self, size, shape, full, color, name): pass

class FigureBuilder(Builder):
    """ The final product."""
    def __init__(self):
        self.new_figure = Figure()

    def build_figure(self, size, shape, full, color, name):
        self.new_figure.size = size
        self.new_figure.shape = shape
        self.new_figure.full = full
        self.new_figure.color = color
        self.new_figure.name = name

    def get_figure(self):
        return self.new_figure

class Figure:
    def __init__(self):
        self.size = None
        self.shape = None
        self.full = None
        self.color = None
        self.name = None

    def get_size(self):
        return self.size

    def get_shape(self):
        return self.shape

    def get_full(self):
        return self.full

    def get_color(self):
        return self.color

    def get_name(self):
        return self.name

director = Director()

"""Figure 1"""
director.construct_figure('high', 'square', 1, 'white', 'f1')
f1 = director.get_result()

"""Figure 2"""
director.construct_figure('high', 'square', 0, 'white', 'f2')
f2 = director.get_result()

"""Figure 3"""
director.construct_figure('low', 'square', 1, 'white', 'f3')
f3 = director.get_result()

"""Figure 4"""
director.construct_figure('low', 'square', 0, 'white', 'f4')
f4 = director.get_result()

"""Figure 5"""
director.construct_figure('high', 'round', 1, 'white', 'f5')
f5 = director.get_result()

"""Figure 6"""
director.construct_figure('high', 'round', 0, 'white', 'f6')
f6 = director.get_result()

"""Figure 7"""
director.construct_figure('low', 'round', 1, 'white', 'f7')
f7 = director.get_result()

"""Figure 8"""
director.construct_figure('low', 'round', 0, 'white', 'f8')
f8 = director.get_result()

"""Figure 9"""
director.construct_figure('high', 'square', 1, 'black', 'f9')
f9 = director.get_result()

"""Figure 10"""
director.construct_figure('high', 'square', 0, 'black', 'f10')
f10 = director.get_result()

"""Figure 11"""
director.construct_figure('low', 'square', 1, 'black', 'f11')
f11 = director.get_result()

"""Figure 12"""
director.construct_figure('low', 'square', 0, 'black', 'f12')
f12 = director.get_result()

"""Figure 13"""
director.construct_figure('high', 'round', 1, 'black', 'f13')
f13 = director.get_result()

"""Figure 14"""
director.construct_figure('high', 'round', 0, 'black', 'f14')
f14 = director.get_result()

"""Figure 15"""
director.construct_figure('low', 'round', 1, 'black', 'f15')
f15 = director.get_result()

"""Figure 16"""
director.construct_figure('low', 'round', 0, 'black', 'f16')
f16 = director.get_result()

figures = [f1, f10, f8, f14, f2, f6, f7, f11, f9, f16, f3, f12, f13, f4, f15, f5]
