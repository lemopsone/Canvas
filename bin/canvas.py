import math
import sys
import time
import os
from bin.config import FPS, BOARD_SIZE, BOARD_CENTER, BOARD_MARKER, DEFAULT_COLOR


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
    looped = list()

    def __init__(self):
        os.system("printf '\e[3;0;0t'")
        os.system(f"printf '\e[8;{BOARD_SIZE + 3};{(BOARD_SIZE + 2) * 2}t'")

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
        cls.__board[y] = list(cls.__board[y][:x]) + [f"\033[1;{color}m" + Board.POINT_MARKER + "\033[0m"] + list(
            cls.__board[y][x + 1:])

    @classmethod
    def clear(cls):
        for _ in range(Board.SIZE + 2):
            Console.write(Console.LINE_UP + Console.LINE_CLEAR)

        cls.__board = [list("＋" + "－" * cls.SIZE + "＋" + '\n')] + \
                      [list("｜" + "　" * cls.SIZE + "｜" + "\n")] * cls.SIZE + \
                      [list("＋" + "－" * cls.SIZE + "＋" + "\n")]

    @classmethod
    def update(cls):
        cls.clear()
        cls.draw()
        for obj in cls.looped:
            obj.move_direction()
        time.sleep(1 / FPS)


class Point:
    def __init__(self, x, y, color=DEFAULT_COLOR):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = None
        self.angle = None
        self.bounce = False
        self.set_change_dir = False
        self.set_bounce = None
        self.step_x = None
        self.step_y = None
        self.place()

    def place(self):
        Board.points[id(self)] = (round(self.x), round(self.y), self.color)

    @staticmethod
    def distance(x, y, x0=BOARD_CENTER, y0=BOARD_CENTER):
        return int(math.sqrt((x - x0) ** 2 + (y - y0) ** 2))

    def set_direction(self, angle, velocity, bounce=False):
        self.angle = angle
        self.velocity = velocity
        self.bounce = bounce
        self.step_x = math.cos(math.radians(self.angle))
        self.step_y = math.sin(math.radians(self.angle))

    def move_direction(self):
        if self.velocity is not None:

            if self.collides() or self.set_change_dir:
                if self.bounce:
                    if not (0 <= self.y + self.step_y * self.velocity < BOARD_SIZE) or self.set_bounce == "y":
                        self.velocity *= -1
                    self.angle = (180 - self.angle)
                    self.step_x = math.cos(math.radians(self.angle))
                    self.step_y = math.sin(math.radians(self.angle))
                else:
                    self.velocity *= -1
                self.set_change_dir = False
            self.x += self.step_x * self.velocity
            self.y += self.step_y * self.velocity
            self.place()

    def move_to(self, x, y):
        if self.inside_borders(x, y, add_self=False):
            self.x = x
            self.y = y
            self.place()

    def move_rel(self, x, y):
        if self.inside_borders(x, y):
            self.x += x
            self.y += y
            self.place()

    def move_dist(self, angle, distance):
        x = distance * math.cos(math.radians(angle))
        y = distance * math.sin(math.radians(angle))
        if self.inside_borders(x, y):
            self.x += x
            self.y += y
            self.place()

    def inside_borders(self, dist_x=0, dist_y=0, add_self=True):
        if add_self:
            return 0 <= self.x + dist_x < BOARD_SIZE and 0 <= self.y + dist_y < BOARD_SIZE
        else:
            return 0 <= dist_x < BOARD_SIZE and 0 <= dist_y < BOARD_SIZE

    def collides(self):
        return not ((0 <= self.x + self.step_x * self.velocity < Board.SIZE) and (
                0 <= self.y + self.step_y * self.velocity < Board.SIZE))

    def loop(self):
        if self.angle is not None:
            if self not in Board.looped:
                Board.looped.append(self)

    def stop(self):
        if self in Board.looped:
            Board.looped.remove(self)


class SetOfPoints:
    def __init__(self, points: list[tuple], color=DEFAULT_COLOR):
        self.set_points = []
        self.angle = None
        self.velocity = None
        self.bounce = False
        self.bounce_dir = ""
        self.set_bounce = ""
        for x, y in points:
            self.set_points.append(Point(x, y, color))
        self.p0 = self.set_points[0]

    def __iter__(self):
        return iter(self.set_points)

    def set_direction(self, angle, velocity, bounce=False):
        self.angle = angle
        self.velocity = velocity
        self.bounce = bounce
        for point in self.set_points:
            point.set_direction(angle, velocity, bounce)

    def move_direction(self):
        if self.angle is not None:
            if any(point.collides() for point in self.set_points):
                if self.bounce:
                    if any(
                            not (0 <= point.y + point.step_y * point.velocity < Board.SIZE) for point in
                            self.set_points):
                        self.set_bounce = "y"
                    else:
                        self.set_bounce = "x"
                for point in self.set_points:
                    point.set_change_dir = True
                    point.set_bounce = self.set_bounce
            for point in self.set_points:
                point.move_direction()
            if isinstance(self, Circle):
                self.x0 += self.p0.velocity * self.p0.step_x
                self.y0 += self.p0.velocity * self.p0.step_y

    def move_rel(self, x, y):
        if all(point.inside_borders(x, y) for point in self.set_points):
            for point in self.set_points:
                point.move_rel(x, y)
            if isinstance(self, Circle):
                self.x0 += x
                self.y0 += y

    def move_dist(self, angle, distance):
        x = distance * math.cos(math.radians(angle))
        y = distance * math.sin(math.radians(angle))
        if all(point.inside_borders(x, y) for point in self.set_points):
            for point in self.set_points:
                point.move_dist(angle, distance)
            if isinstance(self, Circle):
                self.x0 += x
                self.y0 += y

    def loop(self):
        if self.angle is not None:
            if self not in Board.looped:
                Board.looped.append(self)

    def stop(self):
        if self in Board.looped:
            Board.looped.remove(self)


class Circle(SetOfPoints):
    def __init__(self, x0, y0, radius, color=DEFAULT_COLOR):
        self.x0 = x0
        self.y0 = y0
        points = list(self.get_points(x0, y0, radius))
        super().__init__(points, color)

    def move_to(self, x, y):
        dist_x = x - self.x0
        dist_y = y - self.y0
        self.move_rel(dist_x, dist_y)

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


class Line(SetOfPoints):
    def __init__(self, point1: tuple, point2: tuple, color=DEFAULT_COLOR):
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
