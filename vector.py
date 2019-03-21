import math


class Vector2D(tuple):
    """A 2 dimensional vector class"""

    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))

    def __init__(self, x, y):
        super(Vector2D, self).__init__()

    def __add__(self, other):
        return Vector2D(self[0] + other[0], self[1] + other[1])

    __radd__ = __add__

    def __sub__(self, other):
        return Vector2D(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return self[0] * other[0] + self[1] * other[1]
        else:
            return Vector2D(self[0] * other, self[1] * other)

    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vector2D(self[0] * other, self[1] * other)
        raise ValueError

    def __neg__(self):
        return Vector2D(-self[0], -self[1])

    def __abs__(self):
        """Returns the length of the vector."""
        return (self[0] ** 2 + self[1] ** 2) ** 0.5

    def __bool__(self):
        return abs(self) != 0

    def __repr__(self):
        return "(%.2f, %.2f)" % self

    def __getnewargs__(self):
        return self[0], self[1]

    def rotate(self, angle, radians=True):
        """rotate self counterclockwise by angle"""
        perpendicular = -self[1], self[0]
        if not radians:
            angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        return Vector2D(self[0] * c + perpendicular[0] * s, self[1] * c + perpendicular[1] * s)

    def normalize(self):
        """Returns a vector in the same direction of length 1."""
        length = abs(self)
        if length == 0:
            return Vector2D(0, 0)
        else:
            return Vector2D(self[0] / length, self[1] / length)

    def projection(self, other):
        """Returns a vector projected on other vector."""
        if abs(self) == 0 or abs(other) == 0:
            return Vector2D(0, 0)
        else:
            return ((self * other) / abs(other) ** 2) * other

    def reflection(self, other):
        """Returns a vector reflected on other vector."""
        return 2 * self.projection(other) - self

    @staticmethod
    def heading(angle, radians=True):
        if radians:
            return Vector2D(math.cos(angle), math.sin(angle))
        else:
            return Vector2D(math.cos(math.radians(angle)), math.sin(math.radians(angle)))

    def get_angle(self, other, radians=True):
        """Will return the angle between this vector and another vector."""
        if abs(self) == 0 or abs(other) == 0:
            return 0
        if radians:
            return math.atan2(other[1], other[0]) - math.atan2(self[1], self[0])
        else:
            return (360 / (2 * math.pi)) * (math.atan2(other[1], other[0]) - math.atan2(self[1], self[0]))
