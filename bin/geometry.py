import math
import sys
import time
from bin.config import FPS, BOARD_SIZE, BOARD_CENTER, BOARD_MARKER


class Console:
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'

    @staticmethod
    def move_up():
        sys.stdout.write(Console.LINE_UP)

    @staticmethod
    def clear_line():
        sys.stdout.write(Console.LINE_CLEAR)

    @staticmethod
    def write(line):
        sys.stdout.write(str(line))

    @staticmethod
    def stderr(line):
        sys.stderr.write(str(line) + ' ')


class Board:
    __board = None
    SIZE = BOARD_SIZE
    POINT_MARKER = BOARD_MARKER
    points = dict()

    @classmethod
    def draw(cls):
        for x, y in cls.points.values():
            x, y = map(round, (x, y))
            Board.place_point(x, y)
        for line in cls.__board:
            Console.write(line)

    @classmethod
    def place_point(cls, x, y):
        x, y = x + 1, y + 1
        cls.__board[y] = cls.__board[y][:x] + Board.POINT_MARKER + cls.__board[y][x + 1:]

    @classmethod
    def clear(cls):
        for _ in range(Board.SIZE + 2):
            Console.write(Console.LINE_UP + Console.LINE_CLEAR)

        cls.__board = ["＋" + "－" * cls.SIZE + "＋" + '\n'] + \
                      ["｜" + "　" * cls.SIZE + "｜" + "\n"] * cls.SIZE + \
                      ["＋" + "－" * cls.SIZE + "＋" + "\n"]

    @classmethod
    def update(cls):
        cls.clear()
        cls.draw()
        time.sleep(1 / FPS)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.place()

    def place(self):
        Board.points[id(self)] = (self.x, self.y)

    @staticmethod
    def distance(x, y, x0=BOARD_CENTER, y0=BOARD_CENTER):
        return int(math.sqrt((x - x0) ** 2 + (y - y0) ** 2))


class MovingPoint(Point):
    def __init__(self, x, y, angle=0, velocity=1):
        super().__init__(x, y)
        self.angle = angle
        self.velocity = velocity
        self.step_x, self.step_y = self.step()

    def move(self):
        if self.collides():
            self.velocity *= -1
        self.x += self.step_x * self.velocity
        self.y += self.step_y * self.velocity
        self.place()

    def collides(self):
        return not ((0 <= self.x + self.step_x * self.velocity < Board.SIZE) and (
                0 <= self.y + self.step_y * self.velocity < Board.SIZE))

    def step(self):
        step_x = math.cos(math.radians(self.angle))
        step_y = math.sin(math.radians(self.angle))
        return step_x, step_y


class SetOfPoints:
    def __init__(self, points: list[tuple]):
        self.set_points = []
        for x, y in points:
            self.set_points.append(Point(x, y))


class SetOfMovingPoints:
    def __init__(self, points: list[tuple], angle=0, velocity=1):
        self.set_points = []
        self.angle = angle
        self.velocity = velocity
        for x, y in points:
            self.set_points.append(MovingPoint(x, y, angle, velocity))

    def move(self):
        if any(point.collides() for point in self.set_points):
            self.velocity *= -1
            for point in self.set_points:
                point.velocity = self.velocity
        for point in self.set_points:
            point.move()


class Circle(SetOfPoints):
    def __init__(self, x0, y0, radius):
        points = list(self.get_points(x0, y0, radius))
        super().__init__(points)

    @staticmethod
    def get_points(x0, y0, radius):
        circle_points = set()
        for x in range(x0 - radius, x0 + radius + 1):
            y_distance = Circle.circle_equation(x, x0, radius)
            circle_points.add((x, round(y0 - y_distance)))
            circle_points.add((x, round(y0 + y_distance)))
        for y in range(y0 - radius, y0 + radius + 1):
            x_distance = Circle.circle_equation(y, y0, radius)
            circle_points.add((round(x0 - x_distance), y))
            circle_points.add((round(x0 + x_distance), y))
        return circle_points

    @staticmethod
    def circle_equation(a, a0, radius):
        return math.sqrt(radius ** 2 - (a - a0) ** 2)


class MovingCircle(SetOfMovingPoints):
    def __init__(self, x0, y0, radius, angle=0, velocity=1):
        points = list(Circle.get_points(x0, y0, radius))
        super().__init__(points, angle, velocity)
