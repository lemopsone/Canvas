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
        for x, y, color in cls.points.values():
            x, y = map(round, (x, y))
            Board.place_point(x, y, color)
        for line in cls.__board:
            for symbol in line:
                Console.write(symbol)

    @classmethod
    def place_point(cls, x, y, color):
        x, y = x + 1, y + 1
        if color is None:
            cls.__board[y] = list(cls.__board[y][:x]) + list(Board.POINT_MARKER) + list(cls.__board[y][x + 1:])
        else:
            cls.__board[y] = list(cls.__board[y][:x]) + [f"\033[1;{color}m" + Board.POINT_MARKER + "\033[0m"] + list(cls.__board[y][x + 1:])

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
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.color = color
        self.place()

    def place(self):
        Board.points[id(self)] = (self.x, self.y, self.color)

    @staticmethod
    def distance(x, y, x0=BOARD_CENTER, y0=BOARD_CENTER):
        return int(math.sqrt((x - x0) ** 2 + (y - y0) ** 2))


class MovingPoint(Point):
    def __init__(self, x, y, angle=0, velocity=1, color=None):
        super().__init__(x, y, color)
        self.angle = angle
        self.velocity = velocity
        self.step_x, self.step_y = self.step()

    def move(self):
        self.step_x, self.step_y = self.step()
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
    def __init__(self, points: list[tuple], color=None):
        self.set_points = []
        for x, y in points:
            self.set_points.append(Point(x, y, color))


class SetOfMovingPoints:
    def __init__(self, points: list[tuple], angle=0, velocity=1, bounce=False, color=None):
        self.bounce = bounce
        self.set_points = []
        self.angle = angle
        self.velocity = velocity
        for x, y in points:
            self.set_points.append(MovingPoint(x, y, angle, velocity, color))

    def move(self):
        if any(point.collides() for point in self.set_points):
            if self.bounce:
                if any(not (0 <= point.y + point.step_y * point.velocity < Board.SIZE) for point in self.set_points):
                    self.velocity *= -1
                    for point in self.set_points:
                        point.angle = (180 - point.angle)
                        point.velocity = self.velocity
                else:
                    for point in self.set_points:
                        point.angle = (180 - point.angle)
            else:
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
    def __init__(self, x0, y0, radius, angle=0, velocity=1, bounce=False, color=None):
        points = list(Circle.get_points(x0, y0, radius))
        super().__init__(points, angle, velocity, bounce, color)


class Line(SetOfPoints):
    def __init__(self, point1: tuple, point2: tuple, color=None):
        points = list(self.line_equation(*point1, *point2))
        super().__init__(points, color)
        # TO-DO: add line

    @staticmethod
    def line_equation(x1, y1, x2, y2):
        line_points = set()
        if x1 != x2:
            k = (y1 - y2) / (x1 - x2)
            b = y2 - k * x2
            #  y = kx + b, x = (y - b)/k
            for x in range(min(x1, x2), max(x1, x2)):
                y = k * x + b
                line_points.add((x, round(y)))
            for y in range(min(y1, y2), max(y1, y2)):
                x = (y - b) / k
                line_points.add((round(x), y))
        else:
            for y in range(min(y1, y2), max(y1, y2)):
                line_points.add((round(x1), y))
        return line_points


class MovingLine(SetOfMovingPoints):
    def __init__(self, point1, point2, angle=0, velocity=1, bounce=False, color=None):
        points = list(Line.line_equation(*point1, *point2))
        self.angle = angle
        self.velocity = velocity
        super().__init__(points, angle, velocity, bounce, color)
