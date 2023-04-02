from utils import byte_clamp


# Class representing an 8 bit color, clamped to 0 and 255
class Colour:
    def __init__(self, r=0.0, g=0.0, b=0.0):
        self.r = byte_clamp(r)
        self.g = byte_clamp(g)
        self.b = byte_clamp(b)


    def to_tuple(self):
        return (self.r, self.g, self.b)
    

    # Linearly interpolate between this and another Colour by alpha, returned as a new Colour
    def lerp(self, other, alpha):
        r = (self.r * alpha) + (other.r * (1.0 - alpha))
        g = (self.g * alpha) + (other.g * (1.0 - alpha))
        b = (self.b * alpha) + (other.b * (1.0 - alpha))
        return Colour(r, g, b)


    def __str__(self):
        return "Colour({}, {}, {})".format(self.r, self.g, self.b)


    def __repr__(self):
        return "{}, {}, {}".format(self.r, self.g, self.b)
    

    # Fixed length of 3
    def __len__(self):
        return 3
    

    # Force clamp the value to 0 to 255
    def __setattr__(self, name, value):
        super().__setattr__(name, byte_clamp(value))


    def __getitem__(self, index):
        if index == 0:
            return self.r
        elif index == 1:
            return self.g
        elif index == 2:
            return self.b
        else:
            raise IndexError()
        

    def __getitem__(self, index, value):
        if index == 0:
            self.r = byte_clamp(value)
        elif index == 1:
            self.g = byte_clamp(value)
        elif index == 2:
            self.b = byte_clamp(value)
        else:
            raise IndexError()


    def __add__(self, other):
        r = self.r + other.r
        g = self.g + other.g
        b = self.b + other.b
        return Colour(r, g, b)


    def __sub__(self, other):
        r = self.r - other.r
        g = self.g - other.g
        b = self.b - other.b
        return Colour(r, g, b)
    

    # Supports both Colour objects and any single values
    def __mul__(self, other):
        if isinstance(other, Colour):
            r = int(self.r * other.r)
            g = int(self.g * other.g)
            b = int(self.b * other.b)
        elif isinstance(other, int) or isinstance(other, float):
            r = int(self.r * other)
            g = int(self.g * other)
            b = int(self.b * other)
        else:
            raise AttributeError("Colour value cannot be multiplied by type.")
        return Colour(r, g, b)
    

    # Supports both Colour objects and single values
    def __truediv__(self, other):
        if isinstance(other, Colour):
            r = int(self.r / other.r)
            g = int(self.g / other.g)
            b = int(self.b / other.b)
        elif isinstance(other, int) or isinstance(other, float):
            r = int(self.r / other)
            g = int(self.g / other)
            b = int(self.b / other)
        else:
            raise AttributeError("Colour value cannot be divided by type.")
        return Colour(r, g, b)
    

    def __eq__(self, other):
        return (self.r == other.r and self.g == other.g and self.b == other.b)
    

    def __ne__(self, other):
        return (self.r != other.r or self.g != other.g or self.b != other.b)


# Color constants
BLACK  = Colour(0,0,0)
WHITE  = Colour(255,255,255)
RED    = Colour(255,0,0)
YELLOW = Colour(255,255,0)
GREEN  = Colour(0,255,0)